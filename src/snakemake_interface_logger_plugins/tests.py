__author__ = "Cade Mirchandani, Johannes Köster"
__copyright__ = "Copyright 2024, Cade Mirchandani, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from abc import ABC, abstractmethod
from typing import Any, Type
import logging
import uuid

from snakemake_interface_logger_plugins.common import LogEvent

from snakemake_interface_logger_plugins.base import LogHandlerBase
from snakemake_interface_logger_plugins.settings import (
    LogHandlerSettingsBase,
    OutputSettingsLoggerInterface,
)


class MockOutputSettings(OutputSettingsLoggerInterface):
    """Mock implementation of OutputSettingsLoggerInterface for testing."""

    def __init__(self) -> None:
        self.printshellcmds = True
        self.nocolor = False
        self.quiet = None
        self.debug_dag = False
        self.verbose = False
        self.show_failed_logs = True
        self.stdout = False
        self.dryrun = False


class TestLogHandlerBase(ABC):
    """Base test class for logger plugin implementations.

    This class provides a standardized way to test logger plugins.
    Concrete test classes should inherit from this class and implement
    the abstract methods to provide plugin-specific details.

    To add custom event testing, simply add your own test methods:

    Example usage:
        class TestMyLoggerPlugin(TestLogHandlerBase):
            __test__ = True

            def get_log_handler_cls(self) -> Type[LogHandlerBase]:
                return MyLogHandler

            def get_log_handler_settings(self) -> Optional[LogHandlerSettingsBase]:
                return MyLogHandlerSettings(my_param="test_value")

            def test_my_custom_events(self):
                # Test specific events your logger handles
                handler = self._create_handler()

                # Create a record with Snakemake event attributes
                record = logging.LogRecord(
                    name="snakemake", level=logging.INFO,
                    pathname="workflow.py", lineno=1,
                    msg="Job finished", args=(), exc_info=None
                )
                record.event = LogEvent.JOB_FINISHED
                record.job_id = 123

                # Test your handler's behavior
                handler.emit(record)
                # Add assertions for expected behavior
    """

    __test__ = False  # Prevent pytest from running this base class

    @abstractmethod
    def get_log_handler_cls(self) -> Type[LogHandlerBase]:
        """Return the log handler class to be tested.

        Returns:
            The LogHandlerBase subclass to test
        """
        ...

    @abstractmethod
    def get_log_handler_settings(self) -> LogHandlerSettingsBase:
        """Return the settings for the log handler.

        Returns:
            An instance of LogHandlerSettingsBase
        """
        ...

    def _create_handler(self) -> LogHandlerBase:
        """Create and return a handler instance for testing."""
        handler_cls = self.get_log_handler_cls()
        settings = self.get_log_handler_settings()
        common_settings = MockOutputSettings()
        return handler_cls(common_settings=common_settings, settings=settings)

    def test_handler_instantiation(self) -> None:
        """Test that the handler can be properly instantiated."""
        handler = self._create_handler()

        # Test basic properties
        assert isinstance(handler, LogHandlerBase)
        assert isinstance(handler, logging.Handler)
        assert handler.common_settings is not None

    def test_abstract_properties(self) -> None:
        """Test that all abstract properties are implemented and return correct types."""
        handler = self._create_handler()

        # Test abstract properties are implemented
        assert isinstance(handler.writes_to_stream, bool)
        assert isinstance(handler.writes_to_file, bool)
        assert isinstance(handler.has_filter, bool)
        assert isinstance(handler.has_formatter, bool)
        assert isinstance(handler.needs_rulegraph, bool)

    def test_stream_file_exclusivity(self) -> None:
        """Test that handler cannot write to both stream and file."""
        handler = self._create_handler()

        # Test mutual exclusivity of stream and file writing
        if handler.writes_to_stream and handler.writes_to_file:
            # This should have been caught during initialization
            assert False, "Handler cannot write to both stream and file"

    def test_emit_method(self) -> None:
        """Test that handler has a callable emit method."""
        handler = self._create_handler()

        # Test that handler has emit method (required for logging.Handler)
        assert hasattr(handler, "emit")
        assert callable(handler.emit)

    def test_basic_logging(self) -> None:
        """Test basic logging functionality."""
        handler = self._create_handler()
        self._test_basic_logging(handler)

    def test_file_writing_capability(self) -> None:
        """Test file writing capability if enabled."""
        handler = self._create_handler()

        if handler.writes_to_file:
            self._test_file_writing(handler)

    def _test_basic_logging(self, handler: LogHandlerBase) -> None:
        """Test basic logging functionality."""
        # Create a simple log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Test that emit doesn't raise an exception
        try:
            handler.emit(record)
        except Exception as e:
            assert False, f"Handler emit method raised unexpected exception: {e}"

    def _test_file_writing(self, handler: LogHandlerBase) -> None:
        """Test file writing capability if the handler writes to file."""
        # Handler should have baseFilename attribute when writes_to_file is True
        if not hasattr(handler, "baseFilename"):
            assert False, (
                "Handler claims to write to file but has no baseFilename attribute"
            )

        # baseFilename should be a string
        base_filename = getattr(handler, "baseFilename", None)
        assert isinstance(base_filename, str), "baseFilename must be a string"
        assert len(base_filename) > 0, "baseFilename cannot be empty"

    def _create_event_record(
        self,
        event: LogEvent,
        msg: str = "",
        level: int = logging.INFO,
        **extra: Any,
    ) -> logging.LogRecord:
        """Create a LogRecord with Snakemake event attributes for testing.

        This creates a standard logging.LogRecord and attaches the given
        LogEvent and any extra keyword arguments as attributes, mimicking
        how Snakemake constructs log records via the ``extra`` parameter.

        Args:
            event: The LogEvent type for this record.
            msg: The log message string.
            level: The logging level (default: INFO).
            **extra: Additional attributes to set on the record
                     (e.g., ``done=3, total=10`` for PROGRESS events).

        Returns:
            A LogRecord with event and extra attributes set.
        """
        record = logging.LogRecord(
            name="snakemake",
            level=level,
            pathname="test.py",
            lineno=1,
            msg=msg,
            args=(),
            exc_info=None,
        )
        record.event = event  # type: ignore[attr-defined]
        for key, value in extra.items():
            setattr(record, key, value)
        return record

    def test_progress_event(self) -> None:
        """Test that a PROGRESS event can be emitted without error."""
        handler = self._create_handler()
        record = self._create_event_record(
            LogEvent.PROGRESS,
            msg="3 of 10 steps (30%) done",
            done=3,
            total=10,
        )
        handler.emit(record)

    def test_error_event(self) -> None:
        """Test that an ERROR event can be emitted without error."""
        handler = self._create_handler()
        record = self._create_event_record(
            LogEvent.ERROR,
            msg="TestError in rule test_rule",
            level=logging.ERROR,
            exception="TestError",
            location="Snakefile, line 10",
            rule="test_rule",
            traceback="Traceback (most recent call last):\n  ...",
            file="Snakefile",
            line="10",
        )
        handler.emit(record)

    def test_job_info_event(self) -> None:
        """Test that a JOB_INFO event can be emitted without error."""
        handler = self._create_handler()
        record = self._create_event_record(
            LogEvent.JOB_INFO,
            msg="rule test_rule:\n    input: input.txt\n    output: output.txt",
            jobid=1,
            rule_name="test_rule",
            rule_msg="rule test_rule:",
            threads=1,
            input=["input.txt"],
            output=["output.txt"],
            log=[],
            benchmark=[],
            wildcards={"sample": "A"},
            reason="Missing output files: output.txt",
            shellcmd="cat input.txt > output.txt",
            priority=1,
            resources={},
        )
        handler.emit(record)

    def test_job_error_event(self) -> None:
        """Test that a JOB_ERROR event can be emitted without error."""
        handler = self._create_handler()
        record = self._create_event_record(
            LogEvent.JOB_ERROR,
            msg="Error in rule test_rule",
            level=logging.ERROR,
            jobid=1,
            rule_name="test_rule",
            rule_msg="Error in rule test_rule",
            input=["input.txt"],
            output=["output.txt"],
            log=[],
            conda_env=None,
            container_img=None,
            aux={},
            shellcmd="cat input.txt > output.txt",
            indent=False,
        )
        handler.emit(record)

    def test_job_started_event(self) -> None:
        """Test that a JOB_STARTED event can be emitted without error."""
        handler = self._create_handler()
        record = self._create_event_record(
            LogEvent.JOB_STARTED,
            msg="",
            jobs=[1, 2, 3],
        )
        handler.emit(record)

    def test_job_finished_event(self) -> None:
        """Test that a JOB_FINISHED event can be emitted without error."""
        handler = self._create_handler()
        record = self._create_event_record(
            LogEvent.JOB_FINISHED,
            msg="Finished job 1.",
            job_id=1,
        )
        handler.emit(record)

    def test_workflow_started_event(self) -> None:
        """Test that a WORKFLOW_STARTED event can be emitted without error."""
        handler = self._create_handler()
        record = self._create_event_record(
            LogEvent.WORKFLOW_STARTED,
            msg="",
            workflow_id=uuid.uuid4(),
            snakefile="Snakefile",
        )
        handler.emit(record)

    def test_run_info_event(self) -> None:
        """Test that a RUN_INFO event can be emitted without error."""
        handler = self._create_handler()
        record = self._create_event_record(
            LogEvent.RUN_INFO,
            msg="Job stats:\njob          count\n-----------  -------\ntest_rule    5\ntotal        5",
            stats={"test_rule": 5, "total": 5},
        )
        handler.emit(record)

    def test_group_info_event(self) -> None:
        """Test that a GROUP_INFO event can be emitted without error."""
        handler = self._create_handler()
        record = self._create_event_record(
            LogEvent.GROUP_INFO,
            msg="group job 0:",
            group_id=0,
            jobs=[],
        )
        handler.emit(record)

    def test_group_error_event(self) -> None:
        """Test that a GROUP_ERROR event can be emitted without error."""
        handler = self._create_handler()
        record = self._create_event_record(
            LogEvent.GROUP_ERROR,
            msg="Error in group 0",
            level=logging.ERROR,
            groupid=0,
            aux_logs=[],
            job_error_info={},
        )
        handler.emit(record)

    def test_resources_info_event(self) -> None:
        """Test that a RESOURCES_INFO event can be emitted without error."""
        handler = self._create_handler()
        record = self._create_event_record(
            LogEvent.RESOURCES_INFO,
            msg="Provided cores: 4",
            cores=4,
            provided_resources={},
        )
        handler.emit(record)

    def test_shellcmd_event(self) -> None:
        """Test that a SHELLCMD event can be emitted without error."""
        handler = self._create_handler()
        record = self._create_event_record(
            LogEvent.SHELLCMD,
            msg="cat input.txt > output.txt",
            jobid=1,
            shellcmd="cat input.txt > output.txt",
        )
        handler.emit(record)

    def test_debug_dag_event(self) -> None:
        """Test that a DEBUG_DAG event can be emitted without error."""
        handler = self._create_handler()
        record = self._create_event_record(
            LogEvent.DEBUG_DAG,
            msg="candidate job test_rule",
            status="candidate",
            job=None,
            file="output.txt",
            exception=None,
        )
        handler.emit(record)

    def test_rulegraph_event(self) -> None:
        """Test that a RULEGRAPH event can be emitted without error."""
        handler = self._create_handler()
        record = self._create_event_record(
            LogEvent.RULEGRAPH,
            msg="",
            rulegraph={"test_rule": ["dependency_rule"]},
        )
        handler.emit(record)
