__author__ = "Cade Mirchandani, Johannes Köster"
__copyright__ = "Copyright 2024, Cade Mirchandani, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"
from typing import Any, List

logger_plugin_prefix = "snakemake-logger-plugin-"
logger_plugin_module_prefix = logger_plugin_prefix.replace("-", "_")
try:
    from enum import StrEnum, auto
except ImportError:
    from enum import Enum, auto

    class StrEnum(str, Enum):  # type: ignore
        """
        StrEnum implementation for Python < 3.11
        """

        @staticmethod
        def _generate_next_value_(
            name: str, start: int, count: int, last_values: List[Any]
        ) -> Any:
            return name.lower()

        def __str__(self) -> str:
            return self.value

        def __repr__(self) -> str:
            return self.value


# LogEvent to inform formatting and available fields.
class LogEvent(StrEnum):
    RUN_INFO = auto()
    WORKFLOW_STARTED = auto()
    SHELLCMD = auto()
    JOB_INFO = auto()
    JOB_ERROR = auto()
    JOB_STARTED = auto()
    JOB_FINISHED = auto()
    GROUP_INFO = auto()
    GROUP_ERROR = auto()
    RESOURCES_INFO = auto()
    DEBUG_DAG = auto()
    PROGRESS = auto()
    RULEGRAPH = auto()
    ERROR = auto()
