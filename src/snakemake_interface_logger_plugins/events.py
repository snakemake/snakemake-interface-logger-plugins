import uuid
from dataclasses import dataclass, field, fields, MISSING
from logging import LogRecord
from typing import Any, Optional, ClassVar, Self, Mapping, TypeVar, TypedDict
from types import MappingProxyType

from .common import LogEvent


T = TypeVar("T")


def _from_record_default(cls: type[T], record: LogRecord, **kw) -> T:
    """Helper function to implement ``LogEventData.from_record()``.

    Gets attribute values from ``record`` for all fields in dataclass ``cls`` and passes them to the
    ``cls`` constructor. Behavior can be overridden for specific fields by passing their values
    as keyword arguments.
    """
    for fld in fields(cls):
        if fld.name in kw:
            continue
        if hasattr(record, fld.name):
            kw[fld.name] = getattr(record, fld.name)
        elif fld.default is MISSING and fld.default_factory is MISSING:
            raise ValueError(f"LogRecord missing required attribute {fld.name!r}")

    return cls(**kw)


class LogEventData:
    """Data associated with a Snakemake log event.

    Attributes
    ----------
    event
        The type of log event (class attribute).
    """

    event: ClassVar[LogEvent]

    @classmethod
    def from_record(cls, record: LogRecord) -> Self:
        """Create an instance from a LogRecord."""
        if cls is LogEventData:
            raise TypeError(
                f"{cls.__name__} is an abstract base class and cannot be instantiated."
            )
        return _from_record_default(cls, record)


@dataclass
class Error(LogEventData):
    event = LogEvent.ERROR

    exception: Optional[str] = None
    location: Optional[str] = None
    rule: Optional[str] = None
    traceback: Optional[str] = None
    file: Optional[str] = None
    line: Optional[str] = None


@dataclass
class WorkflowStarted(LogEventData):
    event = LogEvent.WORKFLOW_STARTED

    workflow_id: uuid.UUID
    snakefile: Optional[str]

    @classmethod
    def from_record(cls, record: LogRecord) -> Self:
        snakefile = getattr(record, "snakefile", None)
        if snakefile is not None:
            try:
                # Try to convert to string - this should work for PosixPath and other path-like objects
                snakefile = str(snakefile)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Could not convert snakefile to string: {e}")
        return _from_record_default(cls, record, snakefile=snakefile)


@dataclass
class JobInfo(LogEventData):
    event = LogEvent.JOB_INFO

    jobid: int
    rule_name: str
    threads: int
    input: Optional[list[str]] = None
    output: Optional[list[str]] = None
    log: Optional[list[str]] = None
    benchmark: Optional[list[str]] = None
    rule_msg: Optional[str] = None
    wildcards: Optional[dict[str, Any]] = field(default_factory=dict)
    reason: Optional[str] = None
    shellcmd: Optional[str] = None
    priority: Optional[int] = None
    resources: Optional[dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_record(cls, record: LogRecord) -> Self:
        resources = {}
        if hasattr(record, "resources") and hasattr(record.resources, "_names"):  # type: ignore
            resources = {
                name: value
                for name, value in zip(record.resources._names, record.resources)  # type: ignore
                if name not in {"_cores", "_nodes"}
            }

        return _from_record_default(cls, record, resources=resources)


@dataclass
class JobStarted(LogEventData):
    event = LogEvent.JOB_STARTED

    job_ids: list[int]

    @classmethod
    def from_record(cls, record: LogRecord) -> Self:
        jobs = getattr(record, "jobs", [])

        if jobs is None:
            jobs = []
        elif isinstance(jobs, int):
            jobs = [jobs]

        return cls(job_ids=jobs)


@dataclass
class JobFinished(LogEventData):
    event = LogEvent.JOB_FINISHED

    job_id: int


@dataclass
class ShellCmd(LogEventData):
    event = LogEvent.SHELLCMD

    jobid: int
    shellcmd: Optional[str] = None
    rule_name: Optional[str] = None

    @classmethod
    def from_record(cls, record: LogRecord) -> "ShellCmd":
        # Snakemake also inconsistently uses "cmd" instead of "shellcmd" in places
        shellcmd = getattr(record, "shellcmd", None) or getattr(record, "cmd", None)
        return _from_record_default(cls, record, shellcmd=shellcmd)


@dataclass
class JobError(LogEventData):
    event = LogEvent.JOB_ERROR

    jobid: int


@dataclass
class GroupInfo(LogEventData):
    event = LogEvent.GROUP_INFO

    group_id: int
    jobs: list[Any] = field(default_factory=list)


@dataclass
class GroupError(LogEventData):
    event = LogEvent.GROUP_ERROR

    groupid: int
    aux_logs: list[Any] = field(default_factory=list)
    job_error_info: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourcesInfo(LogEventData):
    """Information on resources available to workflow.

    This may be emitted multiple times at the beginning of the workflow, each time with only
    some or possible no attributes set.

    Attributes
    ----------
    nodes
        Number of provided remote nodes (see :attr:`Workflow.nodes`)
    cores
        Number of provided CPU cores.
    provided_resources
        Additional resources (see :attr:`Workflow.global_resources`,
        :attr:`ResourceSettings.resources`).
    """

    event = LogEvent.RESOURCES_INFO

    nodes: Optional[list[str]] = None
    cores: Optional[int] = None
    provided_resources: Optional[dict[str, Any]] = None


@dataclass
class DebugDag(LogEventData):
    event = LogEvent.DEBUG_DAG

    status: Optional[str] = None
    job: Optional[Any] = None
    file: Optional[str] = None
    exception: Optional[str] = None


@dataclass
class Progress(LogEventData):
    """Progress of workflow execution.

    Attributes
    ----------
    done
        Number of completed jobs.
    total
        Total number of jobs to be executed.
    """

    event = LogEvent.PROGRESS

    done: int
    total: int


class RuleGraphNode(TypedDict):
    """
    Attributes
    ----------
    rule
        Name of rule.
    """

    rule: str


class RuleGraphEdge(TypedDict):
    """
    Attributes
    ----------
    source
        Index of source node in list.
    target
        Index of target node in list.
    sourcerule
        Name of source rule.
    targetrule
        Name of target rule.
    """

    source: int
    target: int
    sourcerule: str
    targetrule: str


class RuleGraphDict(TypedDict):
    """Representation of the rule graph in ``RULEGRAPH`` event.

    This is a graph where nodes correspond to unique rules for all jobs to be executed, and an
    an edge is present from rule A to rule B if any job of rule A is a dependency of any job of rule
    B. The nodes list is sorted according to a topological sort of the job graph, using the first
    job for each rule.
    """

    nodes: list[RuleGraphNode]
    edges: list[RuleGraphEdge]


@dataclass
class RuleGraph(LogEventData):
    """Dependency graph of rules for all jobs to be executed.

    This is only emitted if a logging plugin specifically requests it.
    """

    event = LogEvent.RULEGRAPH

    rulegraph: RuleGraphDict


@dataclass
class RunInfo(LogEventData):
    """Information on rules/jobs to be executed.

    Emitted prior to start of workflow execution or during a dry run.

    Attributes
    ----------
    per_rule_job_counts
        Mapping from rule names to the number of jobs to be executed for each.
    total_job_count
        Total number of jobs to be executed.
    """

    event = LogEvent.RUN_INFO

    per_rule_job_counts: dict[str, int] = field(default_factory=dict)
    total_job_count: int = 0

    @classmethod
    def from_record(cls, record: LogRecord) -> "RunInfo":
        all_stats = getattr(record, "stats", {})

        per_rule_job_counts = {k: v for k, v in all_stats.items() if k != "total"}

        total_job_count = all_stats.get("total", 0)
        return cls(
            per_rule_job_counts=per_rule_job_counts, total_job_count=total_job_count
        )


#: Mapping from event types to their associated data classes.
LOG_EVENT_CLASSES: Mapping[LogEvent, type[LogEventData]] = MappingProxyType(
    {
        cls.event: cls
        for cls in [
            Error,
            WorkflowStarted,
            JobInfo,
            JobStarted,
            JobFinished,
            ShellCmd,
            JobError,
            GroupInfo,
            GroupError,
            ResourcesInfo,
            DebugDag,
            Progress,
            RuleGraph,
            RunInfo,
        ]
    }
)
