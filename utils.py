import sys
import datetime


def ppformat(obj: list[dict]) -> str:
    """Pretty print a dictionary or list."""

    return_str = "\n"
    for item in obj:
        return_str += str(item) + ",\n"

    return return_str


def configure_logging(logdir="logs", logname=None, level="DEBUG") -> None:
    """Configure logging settings for the application."""
    import os
    from loguru import logger

    # Create logs directory if it doesn't exist
    os.makedirs(logdir, exist_ok=True)

    # Configure logger
    if logname is not None:
        logfile = os.path.join(logdir, f"{logname}.log")
    else:
        # Use current date and time for the log file name
        current_time = datetime.datetime.now()
        logfile = os.path.join(logdir, f"loguru-{current_time:%Y-%m-%d_%H:%M:%S}.log")

    log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    logger.remove()  # Why does it logs duplicated message? · Issue #208 · Delgan/loguru https://github.com/Delgan/loguru/issues/208
    logger.add(
        sys.stderr,
        level=level,
        format=log_format,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    logger.add(
        logfile,
        level=level,
        format=log_format,
        colorize=False,
        backtrace=True,
        diagnose=True,
    )


def print_table_results(hl1_result, hl2_result, hl3_result) -> None:
    """
    Prints a CSV-formatted table of evaluation metrics (Average Precision, Average Recall, Average F1-score)
    for three sets of results (hl1_result, hl2_result, hl3_result) across different model sizes ('small', 'medium', 'large').

    Each input result should be a dictionary with the following structure:
                "Average Precision": float,
                "Average Recall": float,
                "Average F1-score": float
                "Average Precision": float,
                "Average Recall": float,
                "Average F1-score": float
                "Average Precision": float,
                "Average Recall": float,
                "Average F1-score": float
    E.g.
    {
        "small": {
            "Average Precision": 0.20789208014208005,
            "Average Recall": 0.16795069872507945,
            "Average F1-score": 0.18511736449994046
        },
        "medium": {
            "Average Precision": 0.1622987371245884,
            "Average Recall": 0.11944450093745436,
            "Average F1-score": 0.13745127664571
        },
        "large": {
            "Average Precision": 0.09642341601952588,
            "Average Recall": 0.06692299883888311,
            "Average F1-score": 0.07894318047693434
        }
    }

    The function prints three rows (one for each metric), each containing the values for all three results and all three sizes,
    separated by commas, in the following order:
        hl1_small, hl2_small, hl3_small, hl1_medium, hl2_medium, hl3_medium, hl1_large, hl2_large, hl3_large

    Args:
        hl1_result (dict): Evaluation metrics for the first result set.
        hl2_result (dict): Evaluation metrics for the second result set.
        hl3_result (dict): Evaluation metrics for the third result set.

    Returns:
        None
    """

    table_result = ""
    for m in ["Average Precision", "Average Recall", "Average F1-score"]:
        table_result += (
            f'{hl1_result["small"][m]},{hl2_result["small"][m]},{hl3_result["small"][m]},{hl1_result["medium"][m]},{hl2_result["medium"][m]},{hl3_result["medium"][m]},{hl1_result["large"][m]},{hl2_result["large"][m]},{hl3_result["large"][m]}'
            + "\n"
        )

    print(table_result)
