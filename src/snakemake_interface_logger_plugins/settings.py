__author__ = "Cade Mirchandani, Johannes Köster"
__copyright__ = "Copyright 2024, Cade Mirchandani, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from dataclasses import dataclass

import snakemake_interface_common.plugin_registry.plugin


from abc import ABC
from typing import Optional, Sequence


class OutputSettingsLoggerInterface(ABC):
    printshellcmds: bool
    nocolor: bool
    quiet: Optional[Sequence]
    debug_dag: bool
    verbose: bool
    show_failed_logs: bool
    stdout: bool
    dryrun: bool


@dataclass
class LogHandlerSettingsBase(
    snakemake_interface_common.plugin_registry.plugin.SettingsBase
):
    """Base class for log handler settings.

    Logger handlers can define a subclass of this class,
    named 'LoggerSettings'.
    """

    pass
