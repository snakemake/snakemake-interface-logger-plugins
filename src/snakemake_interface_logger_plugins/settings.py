__author__ = "Cade Mirchandani, Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = (
    "Copyright 2024, Cade Mirchandani, Christopher Tomkins-Tinch, Johannes Köster"
)
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from dataclasses import dataclass, field
from typing import Optional

import snakemake_interface_common.plugin_registry.plugin


@dataclass
class LoggerPluginSettingsBase(
    snakemake_interface_common.plugin_registry.plugin.SettingsBase
):
    """Base class for Logger plugin settings.

    Logger plugins can define a subclass of this class,
    named 'LoggerSettings'.
    """

    pass
