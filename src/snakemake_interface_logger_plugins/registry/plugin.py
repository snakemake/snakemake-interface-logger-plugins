__author__ = "Cade Mirchandani, Johannes Köster"
__copyright__ = "Copyright 2024, Cade Mirchandani, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from dataclasses import dataclass
from typing import Optional, Type
from snakemake_interface_logger_plugins.settings import (
    LogHandlerSettingsBase,
)
from snakemake_interface_logger_plugins import common

from snakemake_interface_common.plugin_registry.plugin import PluginBase


@dataclass
class Plugin(PluginBase):
    log_handler: object
    _logger_settings_cls: Optional[Type[LogHandlerSettingsBase]]
    _name: str

    @property
    def name(self) -> str:
        return self._name

    @property
    def cli_prefix(self) -> str:
        return "logger-" + self.name.replace(common.logger_plugin_module_prefix, "")

    @property
    def settings_cls(self) -> Optional[Type[LogHandlerSettingsBase]]:
        return self._logger_settings_cls
