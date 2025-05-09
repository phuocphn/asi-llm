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
