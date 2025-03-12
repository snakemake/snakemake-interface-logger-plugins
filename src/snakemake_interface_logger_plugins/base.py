__author__ = "Cade Mirchandani, Johannes Köster"
__copyright__ = "Copyright 2024, Cade Mirchandani, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from typing import Optional
from snakemake_interface_logger_plugins.settings import (
    LogHandlerSettingsBase,
    OutputSettingsLoggerInterface,
)
from abc import ABC, abstractmethod
from logging import Handler


class LogHandlerBase(ABC, Handler):
    def __init__(
        self,
        common_settings: OutputSettingsLoggerInterface,
        settings: Optional[LogHandlerSettingsBase],
    ) -> None:
        self.common_settings = common_settings
        self.settings = settings
        self.__post_init__()
        if self.writes_to_stream and self.writes_to_file:
            raise ValueError("A handler cannot write to both stream and file")

    def __post_init__(self) -> None:
        pass

    @property
    @abstractmethod
    def writes_to_stream(self) -> bool:
        """
        Whether this plugin writes to stderr/stdout
        """

    @property
    @abstractmethod
    def writes_to_file(self) -> bool:
        """
        Whether this plugin writes to a file
        """

    @property
    @abstractmethod
    def has_filter(self) -> bool:
        """
        Whether this plugin attaches its own filter
        """

    @property
    @abstractmethod
    def has_formatter(self) -> bool:
        """
        Whether this plugin attaches its own formatter
        """

    @property
    @abstractmethod
    def needs_rulegraph(self) -> bool:
        """
        Whether this plugin requires the DAG rulegraph.
        """
