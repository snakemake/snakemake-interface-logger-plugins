# Snakemake Logger Plugin Interface

This package provides a stable interface for interactions between Snakemake and its logger plugins.

Plugins should implement the following skeleton to comply with this interface.
It is recommended to use Snakemake's poetry plugin to set up this skeleton (and automated testing) within a python package, see https://github.com/snakemake/poetry-snakemake-plugin.

## Overview

```python
from snakemake_interface_logger_plugins.base import LogHandlerBase
from snakemake_interface_logger_plugins.settings import LogHandlerSettingsBase

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LogHandlerSettings(LogHandlerSettingsBase):
    myparam: Optional[int] = field(
        default=None,
        metadata={
            "help": "Some help text",
            # Optionally request that setting is also available for specification
            # via an environment variable. The variable will be named automatically as
            # SNAKEMAKE_LOGGER_<LOGGER-name>_<param-name>, all upper case.
            # This mechanism should ONLY be used for passwords and usernames.
            # For other items, we rather recommend to let people use a profile
            # for setting defaults
            # (https://snakemake.readthedocs.io/en/stable/executing/cli.html#profiles).
            "env_var": False,
            # Optionally specify a function that parses the value given by the user.
            # This is useful to create complex types from the user input.
            "parse_func": ...,
            # If a parse_func is specified, you also have to specify an unparse_func
            # that converts the parsed value back to a string.
            "unparse_func": ...,
            # Optionally specify that setting is required when the LOGGER is in use.
            "required": True,
            # Optionally specify multiple args with "nargs": "+"
        },
    )


class LogHandler(LogHandlerBase):
    def __post_init__(self) -> None:
        # initialize additional attributes
        # Do not overwrite the __init__ method as this is kept in control of the base
        # class in order to simplify the update process.
        # See https://github.com/snakemake/snakemake-interface-logger-plugins/blob/main/src/snakemake_interface_logger_plugins/base.py # noqa: E501
        # for attributes of the base class.
        # In particular, the settings of above LogHandlerSettings class are accessible via
        # self.settings.
        # You also have access to self.common_settings here, which are logging settings supplied by the caller in the form of OutputSettingsLoggerInterface. # noqa: E501
        # See https://github.com/snakemake/snakemake-interface-logger-plugins/blob/main/src/snakemake_interface_logger_plugins/settings.py for more details # noqa: E501
        
        # access settings attributes
        self.settings 
        self.common_settings

    # Here you can override logging.Handler methods to customize logging behavior.
    # For example, you can override the emit() method to control how log records
    # are processed and output. See the Python logging documentation for details:
    # https://docs.python.org/3/library/logging.html#handler-objects

    # LogRecords from Snakemake carry contextual information in the record's attributes
    # Of particular interest is the 'event' attribute, which indicates the type of log information contained
    # See https://github.com/snakemake/snakemake-interface-logger-plugins/blob/2ab84cb31f0b92cf0b7ee3026e15d1209729d197/src/snakemake_interface_logger_plugins/common.py#L33 # noqa: E501
    # For examples on parsing LogRecords, see https://github.com/cademirch/snakemake-logger-plugin-snkmt/blob/main/src/snakemake_logger_plugin_snkmt/parsers.py # noqa: E501

    @property
    def writes_to_stream(self) -> bool:
        # Whether this plugin writes to stderr/stdout.
        # If your plugin writes to stderr/stdout, return
        # true so that Snakemake disables its stderr logging.
        ...

    @property
    def writes_to_file(self) -> bool:
        # Whether this plugin writes to a file.
        # If your plugin writes log output to a file, return
        # true so that Snakemake can report your logfile path at workflow end.
        ...

    @property
    def has_filter(self) -> bool:
        # Whether this plugin attaches its own filter.
        # Return true if your plugin provides custom log filtering logic.
        # If false is returned, Snakemake's DefaultFilter will be attached see: https://github.com/snakemake/snakemake/blob/960f6a89eaa31da6014e810dfcf08f635ac03a6e/src/snakemake/logging.py#L372 # noqa: E501
        # See https://docs.python.org/3/library/logging.html#filter-objects for info on how to define and attach a Filter
        ...

    @property
    def has_formatter(self) -> bool:
        # Whether this plugin attaches its own formatter.
        # Return true if your plugin provides custom log formatting logic.
        # If false is returned, Snakemake's Defaultformatter will be attached see: https://github.com/snakemake/snakemake/blob/960f6a89eaa31da6014e810dfcf08f635ac03a6e/src/snakemake/logging.py#L132 # noqa: E501
        # See https://docs.python.org/3/library/logging.html#formatter-objects for info on how to define and attach a Formatter
        ...

    @property
    def needs_rulegraph(self) -> bool:
        # Whether this plugin requires the DAG rulegraph.
        # Return true if your plugin needs access to the workflow's
        # directed acyclic graph for logging purposes.
        ...

```

## Migrating from `--log-handler-script`

To migrate a log handler script to a logger plugin, follow these steps:

### 1. Understand the differences

**Old approach (`--log-handler-script`):**
- Single function that receives message dictionaries
- Direct access to message fields like `msg['level']`, `msg['name']`, `msg['output']`
- Manual file handling and stderr writing

**New approach (Logger Plugin):**
- Class-based handler inheriting from `LogHandlerBase`
- Integration with Python's logging framework
- Access to structured `LogRecord` objects with event context

### 2. Convert your script function to a plugin class

**Example old script:**
```python
def log_handler(msg):
    if msg['level'] == "job_error" and msg['name'] in ['rule1', 'rule2']:
        logfile = msg['log'][0]
        sys.stderr.write(f"Error in {msg['output'][0]}. See {logfile}\n")
        with open(logfile) as f:
            for line in f:
                sys.stderr.write(f"    {line}")
```

**Converted to plugin:**
```python
from snakemake_interface_logger_plugins.base import LogHandlerBase
from snakemake_interface_logger_plugins.common import LogEvent
from rich.console import Console
import logging

class LogHandler(LogHandlerBase):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.console = Console()
    
    def emit(self, record):
        # Access event type from record
        if hasattr(record, 'event') and record.event == LogEvent.JOB_ERROR:
            # Access job information from record attributes
            if hasattr(record, 'name') and record.name in ['rule1', 'rule2']:
                logfile = record.log[0] if hasattr(record, 'log') else None
                output = record.output[0] if hasattr(record, 'output') else "unknown"
                
                # Use rich console for pretty printing
                self.console.print(f"[red]Error in {output}. See {logfile}[/red]")
                if logfile:
                    try:
                        with open(logfile) as f:
                            for line in f:
                                self.console.print(f"    {line.rstrip()}", style="dim")
                    except FileNotFoundError:
                        self.console.print(f"    Log file {logfile} not found", style="yellow")

    @property
    def writes_to_stream(self) -> bool:
        return True # we're using rich in this plugin to pretty print our logs

    @property
    def writes_to_file(self) -> bool:
        return False  # we're not writing to a log file

    @property
    def has_filter(self) -> bool:
        return True  # we're doing our own log filtering

    @property
    def has_formatter(self) -> bool:
        return True  # we format our own output

    @property
    def needs_rulegraph(self) -> bool:
        return False # we're not using the rulegraph
```

### 3. Key migration points

1. **Message access:** Replace `msg['field']` with `record.field` or `getattr(record, 'field', default)`

2. **Event filtering:** Replace `msg['level'] == "job_error"` with `record.event == LogEvent.JOB_ERROR`

3. **Output method:** Replace direct stderr/stdout calls with your plugin's output handling in the `emit()` method

4. **Error handling:** Add proper exception handling for file operations

5. **Property configuration:** Set the abstract properties to inform Snakemake about your handler's behavior

## Available Log Events

The `LogEvent` enum defines particularly important Snakemake events such as workflow starting, job submission, job failure, etc.  
For each event, a corresponding dataclass is defined in `snakemake_interface_logger_plugins.events`.  
These dataclasses provide a typed interface for accessing event-specific fields from a `LogRecord`.

**To extract event data from a `LogRecord`, use the appropriate dataclass's `from_record()` method.**

### Event Types, Dataclasses, and Typical Fields

| LogEvent                    | Dataclass         | Typical Fields (see class for details)                                                                               |
| --------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------- |
| `LogEvent.ERROR`            | `Error`           | exception, location, rule, traceback, file, line                                                                     |
| `LogEvent.WORKFLOW_STARTED` | `WorkflowStarted` | workflow_id, snakefile                                                                                               |
| `LogEvent.JOB_INFO`         | `JobInfo`         | jobid, rule_name, threads, input, output, log, benchmark, rule_msg, wildcards, reason, shellcmd, priority, resources |
| `LogEvent.JOB_STARTED`      | `JobStarted`      | job_ids                                                                                                              |
| `LogEvent.JOB_FINISHED`     | `JobFinished`     | job_id                                                                                                               |
| `LogEvent.SHELLCMD`         | `ShellCmd`        | jobid, shellcmd, rule_name                                                                                           |
| `LogEvent.JOB_ERROR`        | `JobError`        | jobid                                                                                                                |
| `LogEvent.GROUP_INFO`       | `GroupInfo`       | group_id, jobs                                                                                                       |
| `LogEvent.GROUP_ERROR`      | `GroupError`      | groupid, aux_logs, job_error_info                                                                                    |
| `LogEvent.RESOURCES_INFO`   | `ResourcesInfo`   | nodes, cores, provided_resources                                                                                     |
| `LogEvent.DEBUG_DAG`        | `DebugDag`        | status, job, file, exception                                                                                         |
| `LogEvent.PROGRESS`         | `Progress`        | done, total                                                                                                          |
| `LogEvent.RULEGRAPH`        | `RuleGraph`       | rulegraph                                                                                                            |
| `LogEvent.RUN_INFO`         | `RunInfo`         | per_rule_job_counts, total_job_count                                                                                 |

**Note:** These field lists are guidelines only and may change between versions.  
Always use defensive programming practices like `getattr()` with defaults or `hasattr()` checks when accessing fields.

#### Example: Selecting the Right Dataclass for a LogRecord

```python
from snakemake_interface_logger_plugins.common import LogEvent
from snakemake_interface_logger_plugins import events

def parse_event(record):
    if not hasattr(record, "event"):
        return None

    event = record.event

    # Map LogEvent to the corresponding dataclass
    event_map = {
        LogEvent.ERROR: events.Error,
        LogEvent.WORKFLOW_STARTED: events.WorkflowStarted,
        LogEvent.JOB_INFO: events.JobInfo,
        LogEvent.JOB_STARTED: events.JobStarted,
        LogEvent.JOB_FINISHED: events.JobFinished,
        LogEvent.SHELLCMD: events.ShellCmd,
        LogEvent.JOB_ERROR: events.JobError,
        LogEvent.GROUP_INFO: events.GroupInfo,
        LogEvent.GROUP_ERROR: events.GroupError,
        LogEvent.RESOURCES_INFO: events.ResourcesInfo,
        LogEvent.DEBUG_DAG: events.DebugDag,
        LogEvent.PROGRESS: events.Progress,
        LogEvent.RULEGRAPH: events.RuleGraph,
        LogEvent.RUN_INFO: events.RunInfo,
    }

    dataclass_type = event_map.get(event)
    if dataclass_type is not None:
        return dataclass_type.from_record(record)
    else:
        return None

# Usage in a log handler:
def emit(self, record):
    event_data = parse_event(record)
    if event_data:
        # Now you can access event-specific fields, e.g.:
        if isinstance(event_data, events.JobError):
            print(f"Job error for jobid: {event_data.jobid}")
        elif isinstance(event_data, events.Progress):
            print(f"Progress: {event_data.done}/{event_data.total}")
```