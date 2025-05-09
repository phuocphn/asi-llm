import os
import json
import datetime
import hydra
from omegaconf import DictConfig, OmegaConf
from pathlib import Path
from loguru import logger

from langchain_core.prompts import ChatPromptTemplate
from calc1 import compute_cluster_metrics, average_metrics
from src.netlist import SPICENetlist
from utils import ppformat, configure_logging
from models import load_llms
from prompt_collections.hl1 import (
    prompt_hl1_direct_prompting,
    prompt_hl1_direct_prompting_with_instrucion,
)
from prompt_collections.hl2 import (
    prompt_hl2_direct_prompting_single_subcircuit,
    prompt_hl2_direct_prompting_single_subcircuit_with_instrucion,
)
from prompt_collections.hl3 import (
    prompt_hl3_direct_prompting_multiple_subcircuits_with_instrucion,
    prompt_hl3_direct_prompting_multiple_subcircuits,
)


def llm_invoke(model, prompt, data: SPICENetlist) -> list[str, str]:
    try:
        logger.info(prompt.invoke(data.netlist).to_string())
        chain = prompt | model  # | parser
        output = chain.invoke({"netlist": data.netlist})
        logger.info("output before parsing: " + str(output))
        parsed_data = json.loads(
            output.content[
                output.content.find("<json>")
                + len("<json>") : output.content.find("</json>")
            ]
        )
        assert isinstance(
            parsed_data, list
        ), f"parsed_data invalid type: {type(parsed_data)}"
        parsed_data = [
            (cluster["sub_circuit_name"], cluster["components"])
            for cluster in parsed_data
        ]
        return output.content, parsed_data

    except json.decoder.JSONDecodeError as e:
        logger.error(f"parsing LLM output failed: " + output.content)
        return output.content, None
    except Exception as e:
        logger.error(f"exception: {e}")
        return output, None


def find_subcircuits(
    subset: str = "medium",
    model: str = None,
    prompts: str = None,
    category: str = "single",
    metadata: str = None,
):
    results = []
    max_attempts = 2

    for i in range(1, 101):
        data = SPICENetlist(f"data/asi-fuboco-test/{subset}/{i}/")
        logger.info("netlist #" + str(i))

        num_attempts = 0
        result_dir = f"{metadata['llm_output_dir']}/netlist_{i}"
        while num_attempts < max_attempts:
            try:
                if len(prompts) == 1:
                    outputs = []
                    output, parsed_data = llm_invoke(model, prompts[0], data)
                    parsed_data = parsed_data
                    if output is None or parsed_data is None:
                        raise Exception("LLM output is None")
                    outputs.append(output)
                else:
                    parsed_data = []
                    outputs = []
                    for p in prompts:
                        partial_output, partial_parsed_data = llm_invoke(model, p, data)
                        if partial_output is None or partial_parsed_data is None:
                            raise Exception("LLM (partial) output is None")
                        parsed_data += partial_parsed_data
                        outputs.append(partial_output)
                break
            except Exception as e:
                logger.error(f"exception: {e}")
                num_attempts += 1
                continue

        if num_attempts >= max_attempts:
            logger.info(
                f"can not identify subcircuit in the netlist: data/asi-fuboco-test/{subset}/{i}/"
            )
            results.append({"Precision": 0, "Recall": 0, "F1-score": 0})
            for output_index, output_data in enumerate(outputs):
                with open(f"{result_dir}/output_{output_index}.txt", "w") as fw:
                    fw.write(output_data)
                    fw.write("\n------------------------\n")

            continue

        output = "\n".join(outputs)
        logger.info(f"# output={output}")

        logger.info("------------------------------------")
        logger.info(f"predicted_output: {ppformat(parsed_data)}")

        if category.startswith("HL1"):
            logger.info(f"ground truth: {ppformat(data.hl1_gt)}")
            eval_results = compute_cluster_metrics(parsed_data, data.hl1_gt)
        elif category.startswith("HL2"):
            logger.info(f"ground truth: {ppformat(data.hl2_gt)}")
            eval_results = compute_cluster_metrics(parsed_data, data.hl2_gt)
        elif category.startswith("HL3"):
            logger.info(f"ground truth: {ppformat(data.hl3_gt)}")
            eval_results = compute_cluster_metrics(parsed_data, data.hl3_gt)
        else:
            logger.error(f"unknown category: {category}")
            return

        logger.info(f"{eval_results=}")
        logger.info("------------------------------------")
        results.append(eval_results)

        # Save prompt and netlist data

        Path(result_dir).mkdir(parents=True, exist_ok=True)
        with open(f"{result_dir}/data.txt", "w") as fw:
            fw.write(data.netlist)
            fw.write("\n------------------------\n")
            fw.write("hl1_gt: \n" + ppformat(data.hl1_gt))
            fw.write("\n\n")
            fw.write("hl2_gt: \n" + ppformat(data.hl2_gt))

        with open(f"{result_dir}/gt.json", "w") as fw:
            content = {
                "hl1_gt": data.hl1_gt,
                "hl2_gt": data.hl2_gt,
                "hl3_gt": data.hl3_gt,
            }
            fw.write(json.dumps(content, indent=2))

        for prompt_index, prompt in enumerate(prompts):
            with open(f"{result_dir}/prompt_{prompt_index}.txt", "w") as fw:
                fw.write(prompt.invoke(data.netlist).to_string())

        # Save the output to a file
        for output_index, output_data in enumerate(outputs):
            with open(f"{result_dir}/output_{output_index}.txt", "w") as fw:
                fw.write(output_data)
                fw.write("\n------------------------\n")

        with open(f"{result_dir}/parsed_data.json", "w") as fw:
            fw.write(json.dumps(parsed_data, indent=2))

        with open(f"{result_dir}/eval_results.json", "w") as fw:
            fw.write(json.dumps(eval_results, indent=2))

    return results


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(config: DictConfig) -> None:
    save_dir = f"outputs/{config['result_dir']}/"
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    configure_logging(logdir=save_dir, logname=config["logfile"])
    logger.info(OmegaConf.to_yaml(config) + "\n\n\n")

    if config.eval_llm_set == "opensource_llms":
        eval_models = config.opensource_llms
    elif config.eval_llm_set == "all_llms":
        eval_models = config.all_llms
    else:
        raise ValueError(f"Unknown eval_llm_set: {config.eval_llm_set}")

    instruction_dir = {
        "Differential Pair": "HL2-DiffPair",
        "Current Mirror": "HL2-CM",
        "Inverter": "HL2-Inverter",
    }

    for subset in config.benchmark_subsets:
        for model_name in eval_models:
            model = load_llms(model_name)

            for category in config.categories:
                llm_output_dir = f"{os.path.join(save_dir, model_name, 'llm_outputs',  category, subset )}"
                if not os.path.exists(llm_output_dir):
                    Path(llm_output_dir).mkdir(parents=True, exist_ok=True)

                metadata = {
                    "subset": subset,
                    "model_name": model_name,
                    "category": category,
                    "llm_output_dir": llm_output_dir,
                }

                if category.startswith("HL1"):
                    if config.rule_provided:
                        instruction_path = os.path.join(
                            "outputs",
                            "instruction_generation",
                            model_name,
                            "HL1",
                            "instruction-5.md",
                        )
                        with open(instruction_path, "r") as f:
                            instruction_src = f.read()
                        prompt = prompt_hl1_direct_prompting_with_instrucion(
                            instruction_src
                        )
                        result = average_metrics(
                            find_subcircuits(
                                subset,
                                model,
                                prompts=[prompt],
                                category=category,
                                metadata=metadata,
                            )
                        )

                    else:
                        prompt = prompt_hl1_direct_prompting()
                        result = average_metrics(
                            find_subcircuits(
                                subset,
                                model,
                                prompts=[prompt],
                                category=category,
                                metadata=metadata,
                            )
                        )

                elif category.startswith("HL2"):
                    if config.break_hl2_prompt:
                        prompts = []
                        for sc in config.HL2_subcircuits:
                            if config.rule_provided:
                                instruction_path = os.path.join(
                                    "outputs",
                                    "instruction_generation",
                                    model_name,
                                    instruction_dir[sc],
                                    "instruction-5.md",
                                )
                                with open(instruction_path, "r") as f:
                                    instruction_src = f.read()
                                prompts.append(
                                    prompt_hl2_direct_prompting_single_subcircuit_with_instrucion(
                                        sc, instruction_src
                                    )
                                )
                            else:
                                prompts.append(
                                    prompt_hl2_direct_prompting_single_subcircuit(sc)
                                )

                        result = average_metrics(
                            find_subcircuits(
                                subset,
                                model,
                                prompts=prompts,
                                category=category,
                                metadata=metadata,
                            )
                        )
                elif category.startswith("HL3"):
                    if config.rule_provided:
                        result = None
                        instruction_path = os.path.join(
                            "outputs",
                            "instruction_generation",
                            model_name,
                            "HL3",
                            "instruction-5.md",
                        )
                        with open(instruction_path, "r") as f:
                            instruction_src = f.read()

                        prompt = prompt_hl3_direct_prompting_multiple_subcircuits_with_instrucion(
                            instruction_src
                        )
                        result = average_metrics(
                            find_subcircuits(
                                subset,
                                model,
                                prompts=[prompt],
                                category=category,
                                metadata=metadata,
                            )
                        )
                    else:
                        prompt = prompt_hl3_direct_prompting_multiple_subcircuits()
                        result = average_metrics(
                            find_subcircuits(
                                subset,
                                model,
                                prompts=[prompt],
                                category=category,
                                metadata=metadata,
                            )
                        )

                content = f"**result**: model={model_name},subset={subset},category={category}:{result}"
                logger.info(content)
                with open(os.path.join(save_dir, model_name, "result.txt"), "a") as fw:
                    fw.write(content + "\n")


if __name__ == "__main__":
    main()
