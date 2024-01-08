import logging
import rich.traceback as rich_traceback
import rich.console as rich_console
from rich.logging import RichHandler

rich_traceback.install()
console = rich_console.Console()


def setup_logging(level=logging.INFO) -> None:
    """
    Configures the logging system to use rich.

    Args:
        - level (int, optional): The logging level to set for the root (Defaults to logging.INFO)

    Examples:
        ```Python
        setup_logging(logging.DEBUG)
        # Configures logging to show all DEBUG and higher level logs
        logging.debug("Debug")
        ```
    """

    format_str = "%(message)s"
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[RichHandler()],
    )
