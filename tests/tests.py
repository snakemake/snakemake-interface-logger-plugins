from unittest.mock import MagicMock
from logging import Handler, LogRecord
from typing import Optional, Any
from dataclasses import dataclass, field, fields
import uuid

import pytest

from snakemake_interface_logger_plugins.settings import LogHandlerSettingsBase
from snakemake_interface_logger_plugins.registry import (
    LoggerPluginRegistry,
    LogHandlerBase,
)
from snakemake_interface_common.plugin_registry.tests import TestRegistryBase
from snakemake_interface_common.plugin_registry import PluginRegistryBase
from snakemake_interface_logger_plugins.registry.plugin import Plugin
from snakemake_interface_logger_plugins.common import LogEvent
import snakemake_interface_logger_plugins.events as logevents


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


class TestEvents:
    """Tests for LogEvent enum and related dataclasses."""

    # Example events of each type
    EVENTS = [
        logevents.ErrorEvent(exception="ValueError"),
        logevents.WorkflowStartedEvent(
            workflow_id=uuid.uuid4(),
            snakefile="/path/to/Snakefile",
        ),
        logevents.JobInfoEvent(
            job_id=123,
            rule_name="example_rule",
            threads=4,
            input=["input1.txt", "input2.txt"],
            output=["output.txt"],
            log=["log.txt"],
            benchmark="benchmark.csv",
            wildcards={"foo": "bar"},
        ),
        logevents.JobErrorEvent(job_id=123),
        logevents.JobStartedEvent(job_ids=[123, 321]),
        logevents.JobFinishedEvent(job_id=123),
        logevents.ShellCmdEvent(
            job_id=123,
            shellcmd="echo 'Hello, World!'",
            rule_name="example_rule",
        ),
        logevents.JobErrorEvent(job_id=123),
        logevents.GroupInfoEvent(
            group_id="group1",
            jobs=[object(), object()],  # TODO: Actually mock job objects?
        ),
        logevents.GroupErrorEvent(
            group_id="group1",
        ),
        logevents.ResourcesInfoEvent(
            nodes=["node1", "node2"],
            cores=16,
        ),
        logevents.DebugDagEvent(
            status="status",
        ),
        logevents.ProgressEvent(
            done=5,
            total=10,
        ),
        logevents.RuleGraphEvent(
            rulegraph={
                "nodes": [{"rule": "rule1"}, {"rule": "rule2"}],
                "edges": [
                    {
                        "source": 0,
                        "target": 1,
                        "sourcerule": "rule1",
                        "targetrule": "rule2",
                    }
                ],
            },
        ),
        logevents.RunInfoEvent(
            per_rule_job_counts={
                "rule1": 1,
                "rule2": 2,
            },
            total_job_count=3,
        ),
    ]

    @staticmethod
    def _make_record(msg: str, extra: dict[str, Any]) -> LogRecord:
        record = LogRecord(
            "snakemake.logging", 20, "example.py", 1, msg, (), None, "foo", None
        )
        assert not record.__dict__.keys() & extra.keys()
        record.__dict__.update(extra)
        return record

    def test_conversion(self):
        """Check converting to/from dict/LogRecord."""

        for data in self.EVENTS:
            # To/from extra dict
            extra = data.extra(_foo="bar")
            assert extra["event"] == data.event.value
            assert extra["event_data"] is data
            assert extra["_foo"] == "bar"

            # Check aliases applied
            for fld in fields(data):
                alias = fld.metadata.get("alias")
                if alias is not None:
                    assert extra[alias] == getattr(data, fld.name)
                    assert fld.name not in extra

            # Should return value of event_data key if present
            assert logevents.LogEventData.from_extra(extra) is data

            # Without event_data key, should give equivalent instance
            extra2 = extra.copy()
            del extra2["event_data"]
            assert logevents.LogEventData.from_extra(extra2) == data

            # To/from LogRecord
            record = self._make_record("test", extra)
            assert logevents.LogEventData.from_record(record) is data
            record2 = self._make_record("test", extra2)
            assert logevents.LogEventData.from_record(record2) == data

            # Should work with event as string
            extra3 = extra2.copy()
            extra3["event"] = data.event.value
            assert logevents.LogEventData.from_extra(extra3) == data

        # No event
        assert logevents.LogEventData.from_extra({}) is None
        assert logevents.LogEventData.from_record(self._make_record("test", {})) is None

    def test_class_mapping(self):
        """Test that all LogEventData subclasses are registered in the mapping from LogEvent values."""

        from snakemake_interface_logger_plugins.events import LOG_EVENT_CLASSES

        assert LOG_EVENT_CLASSES.keys() == set(LogEvent)
        for event, cls in LOG_EVENT_CLASSES.items():
            assert cls.event is event

    def test_run_info(self):
        """Test RunInfoEvent conversion."""

        counts = {
            "rule1": 2,
            "rule2": 3,
        }
        total = 5
        stats = {**counts, "total": total}

        # Should be able to create from either
        attrs1 = {
            "per_rule_job_counts": counts,
            "total_job_count": total,
        }
        attrs2 = {
            "stats": stats,
        }

        # From constructor
        data = logevents.RunInfoEvent(**attrs1)
        assert logevents.RunInfoEvent(**attrs2) == data

        # From extra
        assert (
            logevents.RunInfoEvent.from_extra({"event": LogEvent.RUN_INFO, **attrs1})
            == data
        )
        assert (
            logevents.RunInfoEvent.from_extra({"event": LogEvent.RUN_INFO, **attrs2})
            == data
        )

        # Extra should contain stats dict
        extra = data.extra()
        assert extra["stats"] == stats
        assert extra["per_rule_job_counts"] == counts
        assert extra["total_job_count"] == total
