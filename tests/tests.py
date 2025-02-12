import pytest
from unittest.mock import MagicMock
from logging import Handler
from typing import Optional
from dataclasses import dataclass, field
from snakemake_interface_logger_plugins.settings import LogHandlerSettingsBase
from snakemake_interface_logger_plugins.registry import (
    LoggerPluginRegistry,
    LogHandlerBase,
)
from snakemake_interface_common.plugin_registry.tests import TestRegistryBase
from snakemake_interface_common.plugin_registry import PluginRegistryBase
from snakemake_interface_logger_plugins.registry.plugin import Plugin


@dataclass
class MockSettings(LogHandlerSettingsBase):
    """Mock settings for the logger plugin."""

    log_level: Optional[str] = field(
        default=None,
        metadata={
            "help": "set the log level",
            "env_var": False,
            "required": False,
        },
    )


class MockPlugin(LogHandlerBase):
    settings_cls = MockSettings  # Use our mock settings class

    def __init__(self, settings: Optional[LogHandlerSettingsBase] = None):
        if settings is None:
            settings = MockSettings()  # Provide default mock settings
        super().__init__(settings)

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
        """Mock logging handler."""
        return MagicMock(spec=Handler)


class TestRegistry(TestRegistryBase):
    __test__ = True

    @pytest.fixture(autouse=True)
    def reset_registry(self, monkeypatch):
        """Ensure the registry is completely reset for each test."""
        if LoggerPluginRegistry._instance:
            LoggerPluginRegistry._instance.plugins = {}
        LoggerPluginRegistry._instance = None

        registry = LoggerPluginRegistry()
        registry.plugins = {
            "rich": Plugin(
                log_handler=MockPlugin,
                _logger_settings_cls=MockSettings,
                _name="rich",
            )
        }  # Inject the mock plugin

        monkeypatch.setattr(self, "get_registry", lambda: registry)

    def get_registry(self) -> PluginRegistryBase:
        return LoggerPluginRegistry()

    def get_test_plugin_name(self) -> str:
        return "rich"

    def validate_plugin(self, plugin: LogHandlerBase):
        assert plugin.settings_cls is MockSettings  # Ensure settings class is correct

    def validate_settings(
        self, settings: LogHandlerSettingsBase, plugin: LogHandlerBase
    ):
        assert isinstance(settings, MockSettings)
        assert settings.log_level == "info"

    def get_example_args(self):
        return ["--logger-rich-log-level", "info"]
