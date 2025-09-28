__author__ = "Cade Mirchandani, Johannes Köster"
__copyright__ = "Copyright 2024, Cade Mirchandani, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from abc import ABC, abstractmethod
from typing import Type
import logging

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
