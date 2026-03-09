import uuid
from dataclasses import Field, dataclass, field, fields, MISSING
from logging import LogRecord
from typing import Any, Optional, ClassVar, Self, Mapping, TypeVar, TypedDict, TypeAlias
from types import MappingProxyType

from .common import LogEvent


_EventDataT = TypeVar("_EventDataT", bound="LogEventData")
StrMap: TypeAlias = Mapping[str, Any]


#################### Utils ####################


def field_has_default(field: Field) -> bool:
    """Check whether a dataclass field has a default value."""
    return field.default is not MISSING or field.default_factory is not MISSING


def is_namedlist(obj: Any) -> bool:
    """Check whether an object is a Snakemake NamedList.

    (Can't do an isinstance check without importing snakemake)
    """
    return isinstance(obj, list) and hasattr(obj, "_names")


#################### Base class ####################


def _from_extra_default(
    cls: type[_EventDataT], extra: StrMap, /, **kw: Any
) -> _EventDataT:
    """Helper function to implement ``LogEventData._from_extra()``.

    Picks values from ``extra`` for all fields in dataclass ``cls`` and passes them to the ``cls``
    constructor. Behavior can be overridden for specific fields by passing their values as keyword
    arguments.
    """
    for fld in fields(cls):
        if fld.name in kw:
            continue
        name = fld.metadata.get("alias", fld.name)
        if name in extra:
            kw[fld.name] = extra[name]
        elif not field_has_default(fld):
            raise ValueError(f"LogRecord missing required attribute {name!r}")

    return cls(**kw)


@dataclass
class LogEventData:
    """Data associated with a Snakemake log event.

    This class and its subclasses are intended to be integrated directly into the main Snakemake
    library, but the behavior of the :meth:`from_record()` and :meth:`extra()` methods are
    designed to behave consistently before and after this happens.

    Pre-integration: logging functions are called with a manually-constructed ``extra`` dictionary
    of additional attributes to add to the ``LogRecord``. :meth:`from_record()` inspects the
    ``event`` attribute and constructs an instance of the appropriate subclass using the record's
    other attribute values.

    Post-integration: logging code constructs an instance of the subclass directly and calls the
    :meth:`extra()` method to obtain the ``extra`` dictionary to pass to logging functions. This
    includes the instance itself under the ``event_data`` key (which should be the preferred way for
    future code to access the data), but also includes all individual attributes for backward
    compatibility.

    If fields have an ``alias`` key in their metadata, this is used in place of the field's name
    when converting to and from the ``extra`` dictionary or a ``LogRecord`` instance. This provides
    more consistent naming on the dataclasses while maintaining compatibility with existing logging
    code that reads the old attribute names from the ``LogRecord``.

    Attributes
    ----------
    event
        The type of log event (class attribute).
    """

    event: ClassVar[LogEvent]

    def __init__(self) -> None:
        # Allow super().__init__() in subclasses even if it doesn't do anything
        if type(self) is LogEventData:
            raise TypeError(
                f"{type(self).__name__} is an abstract base class and cannot be instantiated."
            )

    @staticmethod
    def from_record(record: LogRecord) -> "LogEventData | None":
        """Create an instance from a LogRecord.

        See :meth:`from_extra` for details. Returns ``None`` if record does not have an
        event attached.
        """
        return LogEventData.from_extra(record.__dict__)

    @classmethod
    def from_extra(cls, extra: StrMap) -> "LogEventData | None":
        """Create from dictionary of extra log record attributes.

        If ``extra`` has an ``'event_data'`` key, its value is returned directly. Otherwise selects
        the appropriate subclass based on the ``'event'`` key/attribute. Returns None if no event
        is present.
        """
        event_data = extra.get("event_data", None)
        if event_data is not None:
            return event_data

        event = extra.get("event", None)
        if event is None:
            return None

        # Ensure event is a LogEvent (also convert plain strings)
        try:
            event = LogEvent(event)
        except ValueError:
            return None

        cls = LOG_EVENT_CLASSES[event]
        return cls._from_extra(extra)

    @classmethod
    def _from_extra(cls, extra: StrMap) -> Self:
        """Subclass-specific implementation of ``from_extra()``."""
        return _from_extra_default(cls, extra)

    def extra(self, **kw: Any) -> dict[str, Any]:
        """Convert to dictionary of extra log record attributes.

        The result can be passed as the ``extra`` parameter of logging methods to add the
        instance's attributes to the log record. Also includes the instance itself under
        ``"event_data"`` and its ``LogEvent`` under ``"event"``.

        Any additional keyword arguments are added to the resulting dictionary.
        """
        extra = self._extra()
        extra["event"] = self.event
        extra["event_data"] = self
        extra.update(kw)
        return extra

    def _extra(self) -> dict[str, Any]:
        """To be overridden by subclasses if needed."""
        return {
            fld.metadata.get("alias", fld.name): getattr(self, fld.name)
            for fld in fields(self)
        }


#################### Event classes ####################


@dataclass
class ErrorEvent(LogEventData):
    event = LogEvent.ERROR

    exception: Optional[str] = None
    location: Optional[str] = None
    rule: Optional[str] = None
    traceback: Optional[str] = None
    file: Optional[str] = None
    line: Optional[str] = None


@dataclass
class WorkflowStartedEvent(LogEventData):
    event = LogEvent.WORKFLOW_STARTED

    workflow_id: uuid.UUID
    snakefile: Optional[str]

    @classmethod
    def _from_extra(cls, extra: StrMap) -> Self:
        snakefile = extra.get("snakefile", None)
        if snakefile is not None:
            try:
                # Try to convert to string - this should work for PosixPath and other path-like objects
                snakefile = str(snakefile)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Could not convert snakefile to string: {e}")
        return _from_extra_default(cls, extra, snakefile=snakefile)


@dataclass
class JobInfoEvent(LogEventData):
    event = LogEvent.JOB_INFO

    job_id: int = field(metadata={"alias": "jobid"})
    rule_name: str
    threads: int
    input: Optional[list[str]] = None
    output: Optional[list[str]] = None
    log: Optional[list[str]] = None
    benchmark: Optional[str] = None
    rule_msg: Optional[str] = None
    wildcards: Optional[dict[str, Any]] = field(default_factory=dict)
    reason: Optional[str] = None
    shellcmd: Optional[str] = None
    priority: Optional[int] = None
    resources: Optional[dict[str, Any]] = field(default_factory=dict)
    local: Optional[bool] = None
    is_checkpoint: Optional[bool] = None
    is_handover: Optional[bool] = None

    @classmethod
    def _from_extra(cls, extra: StrMap) -> Self:
        resources_obj = extra.get("resources", None)

        if resources_obj is None:
            resources = {}
        elif is_namedlist(resources_obj):
            resources = dict(resources_obj.items())
        elif isinstance(resources_obj, Mapping):
            resources = dict(resources_obj)
        else:
            raise TypeError("resources must be a Mapping, NamedList, or None")

        resources = {
            name: value
            for name, value in resources.items()
            if name not in {"_cores", "_nodes"}
        }

        return _from_extra_default(cls, extra, resources=resources)


@dataclass
class JobStartedEvent(LogEventData):
    event = LogEvent.JOB_STARTED

    job_ids: list[int] = field(metadata={"alias": "jobs"})


@dataclass
class JobFinishedEvent(LogEventData):
    event = LogEvent.JOB_FINISHED

    job_id: int


@dataclass
class ShellCmdEvent(LogEventData):
    event = LogEvent.SHELLCMD

    job_id: Optional[int] = field(default=None, metadata={"alias": "jobid"})
    shellcmd: Optional[str] = None
    rule_name: Optional[str] = None

    @classmethod
    def _from_extra(cls, extra: StrMap) -> "ShellCmdEvent":
        # Snakemake also inconsistently uses "cmd" instead of "shellcmd" in places
        shellcmd = extra.get("shellcmd", None) or extra.get("cmd", None)
        return _from_extra_default(cls, extra, shellcmd=shellcmd)


@dataclass
class JobErrorEvent(LogEventData):
    event = LogEvent.JOB_ERROR

    job_id: int = field(metadata={"alias": "jobid"})


@dataclass
class GroupInfoEvent(LogEventData):
    event = LogEvent.GROUP_INFO

    group_id: str
    jobs: list[Any] = field(default_factory=list)


@dataclass
class GroupErrorEvent(LogEventData):
    event = LogEvent.GROUP_ERROR

    group_id: str = field(metadata={"alias": "groupid"})
    aux_logs: list[Any] = field(default_factory=list)
    job_error_info: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ResourcesInfoEvent(LogEventData):
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
class DebugDagEvent(LogEventData):
    event = LogEvent.DEBUG_DAG

    status: Optional[str] = None
    job: Optional[Any] = None
    file: Optional[str] = None
    exception: Optional[BaseException] = None


@dataclass
class ProgressEvent(LogEventData):
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
class RuleGraphEvent(LogEventData):
    """Dependency graph of rules for all jobs to be executed.

    This is only emitted if a logging plugin specifically requests it.
    """

    event = LogEvent.RULEGRAPH

    rulegraph: RuleGraphDict


@dataclass
class RunInfoEvent(LogEventData):
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

    per_rule_job_counts: dict[str, int]
    total_job_count: int

    def __init__(
        self,
        per_rule_job_counts: dict[str, int] | None = None,
        total_job_count: int | None = None,
        stats: dict[str, int] | None = None,
    ):
        """
        Parameters
        ----------
        per_rule_job_counts
        total_job_count
        stats
            From :meth:`DAG.stats()`. Provides defaults for previous two parameters.
        """
        if per_rule_job_counts is not None:
            self.per_rule_job_counts = per_rule_job_counts
        elif stats is not None:
            self.per_rule_job_counts = {k: v for k, v in stats.items() if k != "total"}
        else:
            self.per_rule_job_counts = {}

        if total_job_count is not None:
            self.total_job_count = total_job_count
        elif stats is not None:
            self.total_job_count = stats.get(
                "total", sum(self.per_rule_job_counts.values())
            )
        else:
            self.total_job_count = sum(self.per_rule_job_counts.values())

    @classmethod
    def _from_extra(cls, extra: StrMap) -> "RunInfoEvent":
        return cls(
            per_rule_job_counts=extra.get("per_rule_job_counts"),
            total_job_count=extra.get("total_job_count"),
            stats=extra.get("stats"),
        )

    def _extra(self) -> dict[str, Any]:
        extra = super()._extra()
        # Add "stats" key for compatibility
        stats = dict(self.per_rule_job_counts)
        stats["total"] = self.total_job_count
        extra["stats"] = stats
        return extra


#: Mapping from event types to their associated data classes.
LOG_EVENT_CLASSES: Mapping[LogEvent, type[LogEventData]] = MappingProxyType(
    {
        cls.event: cls
        for cls in [
            ErrorEvent,
            WorkflowStartedEvent,
            JobInfoEvent,
            JobStartedEvent,
            JobFinishedEvent,
            ShellCmdEvent,
            JobErrorEvent,
            GroupInfoEvent,
            GroupErrorEvent,
            ResourcesInfoEvent,
            DebugDagEvent,
            ProgressEvent,
            RuleGraphEvent,
            RunInfoEvent,
        ]
    }
)
