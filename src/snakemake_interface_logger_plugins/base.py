__author__ = "Cade Mirchandani, Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = (
    "Copyright 2024, Cade Mirchandani, Christopher Tomkins-Tinch, Johannes Köster"
)
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from abc import ABC, abstractmethod
from typing import Optional
from snakemake_interface_logger_plugins.settings import LoggerPluginSettingsBase
from logging import Handler


class LoggerPluginBase(ABC):
    def __init__(
        self,
        settings: Optional[LoggerPluginSettingsBase],
    ) -> None:
        self.settings = settings
        self.__post__init()

    def __post__init(self) -> None:
        pass

    @abstractmethod
    def create_handler(
        self,
        quiet,
        printshellcmds: bool,
        printreason: bool,
        debug_dag: bool,
        nocolor: bool,
        stdout: bool,
        debug: bool,
        mode,
        show_failed_logs: bool,
        dryrun: bool,
    ) -> Handler:
        """
        This function should be defined by the logging plugin and return an instance of a subclass of logging.Handler,
        with formatter and filter already set. If those are not set, then the Snakemake defaults will be used.

        Returns:
            Handler: The handler instance.
        """
        pass
