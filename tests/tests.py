import pytest
from snakemake_interface_logger_plugins.registry import (
    LoggerPluginRegistry,
    LogHandlerBase,
)
from snakemake_interface_common.plugin_registry.tests import TestRegistryBase
from snakemake_interface_common.plugin_registry import PluginRegistryBase
from snakemake_interface_logger_plugins.registry.plugin import Plugin
from snakemake_interface_logger_plugins.tests import TestLogHandlerBase


# Import the actual rich plugin
from snakemake_logger_plugin_rich import LogHandler as RichLogHandler
from snakemake_interface_logger_plugins.settings import LogHandlerSettingsBase
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MockRichSettings(LogHandlerSettingsBase):
    """Mock settings for the rich logger plugin."""

    log_level: Optional[str] = field(
        default=None,
        metadata={
            "help": "set the log level",
            "env_var": False,
            "required": False,
        },
    )


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
                log_handler=RichLogHandler,
                _logger_settings_cls=MockRichSettings,
                _name="rich",
            )
        }  # Inject the rich plugin

        monkeypatch.setattr(self, "get_registry", lambda: registry)

    def get_registry(self) -> PluginRegistryBase:
        return LoggerPluginRegistry()

    def get_test_plugin_name(self) -> str:
        return "rich"

    def validate_plugin(self, plugin: LogHandlerBase):
        assert (
            plugin.settings_cls is MockRichSettings
        )  # Ensure settings class is correct

    def validate_settings(
        self, settings: LogHandlerSettingsBase, plugin: LogHandlerBase
    ):
        assert isinstance(settings, MockRichSettings)
        assert settings.log_level == "info"

    def get_example_args(self):
        return ["--logger-rich-log-level", "info"]


class TestConcreteRichPlugin(TestLogHandlerBase):
    """Concrete test using the actual rich plugin to verify the abstract test class works."""

    __test__ = True

    def get_log_handler_cls(self):
        """Return the rich log handler class."""
        return RichLogHandler

    def get_log_handler_settings(self):
        """Return the rich settings with default values for testing."""
        return MockRichSettings()
