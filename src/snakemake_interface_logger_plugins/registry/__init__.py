__author__ = "Cade Mirchandani, Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = (
    "Copyright 2024, Cade Mirchandani, Christopher Tomkins-Tinch, Johannes Köster"
)
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

import types
from typing import List, Mapping

from snakemake_interface_logger_plugins.settings import (
    LoggerPluginSettingsBase,
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
    LoggerPluginBase,
)


class LoggerPluginRegistry(PluginRegistryBase):
    """This class is a singleton that holds all registered executor plugins."""

    @property
    def module_prefix(self) -> str:
        return common.logger_plugin_module_prefix

    def load_plugin(self, name: str, module: types.ModuleType) -> Plugin:
        """Load a plugin by name."""

        return Plugin(
            _name=name,
            logger_plugin=module.LoggerPlugin,
            _logger_settings_cls=getattr(module, "LoggerPluginSettings", None),
        )

    def expected_attributes(self) -> Mapping[str, AttributeType]:
        return {
            "LoggerPluginSettings": AttributeType(
                cls=LoggerPluginSettingsBase,
                mode=AttributeMode.OPTIONAL,
                kind=AttributeKind.CLASS,
            ),
            "LoggerPlugin": AttributeType(
                cls=LoggerPluginBase,
                mode=AttributeMode.REQUIRED,
                kind=AttributeKind.CLASS,
            ),
        }
