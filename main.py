import os
import json
import datetime
import hydra
from omegaconf import DictConfig, OmegaConf
from pathlib import Path
from loguru import logger

from langchain_core.prompts import ChatPromptTemplate
from calc1 import compute_cluster_metrics, compute_cluster_metrics_hl1, average_metrics
from src.netlist import SPICENetlist
from src.kb import get_knowledge_base
from utils import ppformat, configure_logging
from models import load_ollama, load_deepseek
from prompt_collections.hl1 import (
    create_prompt_hl1,
)
from prompt_collections.hl2 import (
    create_prompt_hl2,
    create_prompt_hl2_with_multiple_subcircuit_identification_and_fixed_rule_provided,
    create_prompt_hl2_with_target_single_subcircuit_only,
    create_prompt_hl2_with_target_single_subcircuit_only_and_fixed_rule_provided,
)

# -----


def llm_invoke(model, prompt, data: SPICENetlist) -> list[str, str]:
    try:
        # prompt = create_prompt_hl2()
        logger.info(prompt.invoke(data.netlist).to_string())
        chain = prompt | model  # | parser
        output = chain.invoke({"netlist": data.netlist})
        parsed_data = json.loads(
            output.content[
                output.content.find("<json>")
                + len("<json>") : output.content.find("</json>")
            ]
        )
        assert isinstance(parsed_data, list), "parsed data is not a list: " + str(
            parsed_data
        )
        return output, parsed_data
    except json.decoder.JSONDecodeError as e:
        logger.error(f"parsing LLM output failed: " + output.content)
        return None, None

    except Exception as e:
        logger.error(f"exception: {e}")
        return None, None


def identify_devices(
    subset="medium", model=None, prompts=None, category="single", metadata=None
):
    results = []
    i = 1
    max_i = 101

    num_attempts = 0
    max_attempts = 5

    while i < max_i and num_attempts < max_attempts:
        data = SPICENetlist(f"data/benchmark-asi-100/{subset}/{i}/")
        logger.info("netlist #" + str(i))

        try:
            if len(prompts) == 1:
                outputs = []
                output, parsed_data = llm_invoke(model, prompts[0], data)
                parsed_data = parsed_data
                if output is None or parsed_data is None:
                    raise Exception("LLM output is None")
                outputs.append(output.content)
            else:
                parsed_data = []
                outputs = []
                for p in prompts:
                    partial_output, partial_parsed_data = llm_invoke(model, p, data)
                    if output is not None and partial_parsed_data is not None:
                        parsed_data += partial_parsed_data
                        outputs.append(partial_output.content)
        except Exception as e:
            logger.error(f"exception: {e}")
            num_attempts += 1
            continue

        output = "\n".join(outputs)
        logger.info(f"# output={output}")

        logger.info("------------------------------------")
        logger.info(f"predicted_output: {ppformat(parsed_data)}")

        if category == "single":
            logger.info(f"ground truth: {ppformat(data.hl1_gt)}")
            eval_results = compute_cluster_metrics_hl1(
                predicted=parsed_data, ground_truth=data.hl1_gt
            )
        elif category == "pair":
            logger.info(f"ground truth: {ppformat(data.hl2_gt)}")
            eval_results = compute_cluster_metrics(
                predicted=parsed_data, ground_truth=data.hl2_gt
            )
        else:
            logger.error(f"unknown category: {category}")
            return

        logger.info(f"{eval_results=}")
        logger.info("------------------------------------")
        results.append(eval_results)

        num_attempts = 0

        # Save prompt and netlist data
        save_dir = f"{metadata['llm_output_dir']}/netlist_{i}"

        Path(save_dir).mkdir(parents=True, exist_ok=True)
        with open(f"{save_dir}/data.txt", "w") as fw:
            fw.write(data.netlist)
            fw.write("\n------------------------\n")
            fw.write("hl1_gt: \n" + ppformat(data.hl1_gt))
            fw.write("\n\n")
            fw.write("hl2_gt: \n" + ppformat(data.hl2_gt))

        with open(f"{save_dir}/gt.json", "w") as fw:
            content = {"hl1_gt": data.hl1_gt, "hl2_gt": data.hl2_gt}
            fw.write(json.dumps(content, indent=2))

        for prompt_index, prompt in enumerate(prompts):
            with open(f"{save_dir}/prompt_{prompt_index}.txt", "w") as fw:
                fw.write(prompt.invoke(data.netlist).to_string())

        # Save the output to a file
        for output_index, output_data in enumerate(outputs):
            with open(f"{save_dir}/output_{output_index}.txt", "w") as fw:
                fw.write(output_data)
                fw.write("\n------------------------\n")

        with open(f"{save_dir}/parsed_data.json", "w") as fw:
            fw.write(json.dumps(parsed_data, indent=2))

        with open(f"{save_dir}/eval_results.json", "w") as fw:
            fw.write(json.dumps(eval_results, indent=2))

        i += 1

    if num_attempts < max_attempts:
        return results
    else:
        return [{"Precision": 0, "Recall": 0, "F1-score": 0}]


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(config: DictConfig) -> None:
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    save_dir = f"outputs/main/{now}"

    # create directory if it doesn't exist
    if not os.path.exists(save_dir):
        Path(save_dir).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(os.path.join(save_dir, "results")):
        os.makedirs(os.path.join(save_dir, "results"))
        Path(os.path.join(save_dir, "results")).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(os.path.join(save_dir, "llm_outputs")):
        Path(os.path.join(save_dir, "llm_outputs")).mkdir(parents=True, exist_ok=True)

    configure_logging(logdir=save_dir)

    logger.info(OmegaConf.to_yaml(config) + "\n\n\n")

    if config.eval_llms == "small":
        llm_models = config.small_llms
    elif config.eval_llms == "medium":
        llm_models = config.medium_llms
    elif config.eval_llms == "all":
        llm_models = config.all_llms
    elif config.eval_llms == "proprietary":
        llm_models = config.proprietary_llms
    else:
        raise ValueError(f"Unknown llm_models: {config.eval_llms}")

    for subset in config.benchmark_subsets:
        for model_id in llm_models:
            if config.eval_llms == "proprietary" and model_id == "deepseek":
                llm = load_deepseek()
            else:
                llm = load_ollama(model_id)
            for category in config.categories:  # ["single", "pair"]:
                llm_output_dir = f"{os.path.join(save_dir, 'llm_outputs')}/subset_{subset}_{model_id}_{category}"
                if not os.path.exists(llm_output_dir):
                    os.makedirs(llm_output_dir)

                metadata = {
                    "subset": subset,
                    "model_id": model_id,
                    "category": category,
                    "llm_output_dir": llm_output_dir,
                }

                if category == "single":
                    prompt = create_prompt_hl1()
                    result = average_metrics(
                        identify_devices(
                            subset,
                            llm,
                            prompts=[prompt],
                            category=category,
                            metadata=metadata,
                        )
                    )

                elif category == "pair":
                    if config.break_hl2_prompt:
                        prompts = []
                        for subcircuit_name, abbreviation in config.subcircuits.items():
                            if config.rule_provided:
                                prompt = create_prompt_hl2_with_target_single_subcircuit_only_and_fixed_rule_provided(
                                    subcircuit_name=subcircuit_name,
                                    abbreviation=abbreviation,
                                )
                                prompts.append(prompt)
                            else:
                                prompt = create_prompt_hl2_with_target_single_subcircuit_only(
                                    subcircuit_name=subcircuit_name,
                                    abbreviation=abbreviation,
                                )
                                prompts.append(prompt)

                        result = average_metrics(
                            identify_devices(
                                subset,
                                llm,
                                prompts=prompts,
                                category=category,
                                metadata=metadata,
                            )
                        )
                    else:
                        if config.rule_provided:
                            prompt = create_prompt_hl2_with_multiple_subcircuit_identification_and_fixed_rule_provided(
                                config.rule_src
                            )
                            result = average_metrics(
                                identify_devices(
                                    subset,
                                    llm,
                                    prompts=[prompt],
                                    category=category,
                                    metadata=metadata,
                                )
                            )

                        else:
                            prompt = create_prompt_hl2()
                            result = average_metrics(
                                identify_devices(
                                    subset,
                                    llm,
                                    prompts=[prompt],
                                    category=category,
                                    metadata=metadata,
                                )
                            )

                content = f"**result**: model={model_id},category={category}:{result}"
                logger.info(content)
                with open(os.path.join(save_dir, "result.txt"), "a") as fw:
                    fw.write(content + "\n")


if __name__ == "__main__":
    main()
