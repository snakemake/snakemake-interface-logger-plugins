__author__ = "Cade Mirchandani, Johannes Köster"
__copyright__ = "Copyright 2024, Cade Mirchandani, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from dataclasses import dataclass

import snakemake_interface_common.plugin_registry.plugin


@dataclass
class LogHandlerSettingsBase(
    snakemake_interface_common.plugin_registry.plugin.SettingsBase
):
    """Base class for log handler settings.

    Logger handlers can define a subclass of this class,
    named 'LoggerSettings'.
    """

    pass
