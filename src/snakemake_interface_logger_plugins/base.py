__author__ = "Cade Mirchandani, Johannes Köster"
__copyright__ = "Copyright 2024, Cade Mirchandani, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from typing import Optional
from snakemake_interface_logger_plugins.settings import LogHandlerSettingsBase
from logging import Handler


class LogHandlerBase(Handler):
    def __init__(
        self,
        settings: Optional[LogHandlerSettingsBase],
    ) -> None:
        self.settings = settings
        self.__post__init()

    def __post__init(self) -> None:
        pass
