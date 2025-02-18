__author__ = "Cade Mirchandani, Johannes Köster"
__copyright__ = "Copyright 2024, Cade Mirchandani, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

import types
from typing import Mapping

from snakemake_interface_logger_plugins.settings import (
    LogHandlerSettingsBase,
)
from snakemake_interface_common.plugin_registry.attribute_types import (
    AttributeKind,
    AttributeMode,
    AttributeType,
)
from snakemake_interface_logger_plugins.registry.plugin import Plugin
from snakemake_interface_common.plugin_registry import PluginRegistryBase
from snakemake_interface_logger_plugins import common
from snakemake_interface_logger_plugins.base import (
    LogHandlerBase,
)


class LoggerPluginRegistry(PluginRegistryBase):
    """This class is a singleton that holds all registered logger plugins."""

    @property
    def module_prefix(self) -> str:
        return common.logger_plugin_module_prefix

    def load_plugin(self, name: str, module: types.ModuleType) -> Plugin:
        """Load a plugin by name."""

        return Plugin(
            _name=name,
            log_handler=module.LogHandler,
            _logger_settings_cls=getattr(module, "LogHandlerSettings", None),
        )

    def expected_attributes(self) -> Mapping[str, AttributeType]:
        return {
            "LogHandlerSettings": AttributeType(
                cls=LogHandlerSettingsBase,
                mode=AttributeMode.OPTIONAL,
                kind=AttributeKind.CLASS,
            ),
            "LogHandler": AttributeType(
                cls=LogHandlerBase,
                mode=AttributeMode.REQUIRED,
                kind=AttributeKind.CLASS,
            ),
        }
