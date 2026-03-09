from __future__ import annotations

import os
import logging

from typing import Literal
from pathlib import Path

from deply.core.base_plugins.base import BasePlugin
from deply.core.base_plugins.uv.uv import UVPlugin
from deply.utils.utils import discover_plugins, resolve_user_dir

#
# APP
# # # # # # # #
APP_NAME = "deply"
DEV_MODE = os.getenv("DEPLY_ENV", "production").lower() == "development"
type packageType = Literal["dev", "optional", "prod"]

#
# PATHS
# # # # # # # #
USER_HOME = Path.home()
DEPLY_HOME = resolve_user_dir(APP_NAME, dev_mode=DEV_MODE)
USER_LOG_DIR = DEPLY_HOME / "logs"
USER_CONFIG_DIR = DEPLY_HOME / "config"
USER_DATA_DIR = DEPLY_HOME / "data"

#
# LOGGING
# # # # # # # #
LOG_DIR = f"{APP_NAME}./logs"
LOG_FORMAT = "[%(asctime)s][%(levelname)s][%(name)s][%(message)s]"
LOG_DATE_FORMAT = "%Y-%m-%d][%H:%M:%S"
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5 MB per file
LOG_BACKUP_COUNT = 3
LOG_FILE_NAME = f"{APP_NAME}.log"
LOG_JSONL_FILE_NAME = f"{APP_NAME}.jsonl"
LOG_LEVEL = logging.INFO

#
# PLUGINS
# # # # # # # #
BUILTIN_PLUGINS: dict[str, type[BasePlugin]] = {
    "uv": UVPlugin,
}

# Single registry used by the CLI and run_handler.
SUPPORTED_PLUGINS: dict[str, type[BasePlugin]] = discover_plugins(BUILTIN_PLUGINS)

#
# TUI
# # # # # # # #
APP_BANNER = r"""
[bold cyan]  ____             _
 |  _ \  ___ _ __ | |_   _
 | | | |/ _ \ '_ \| | | | |
 | |_| |  __/ |_) | | |_| |
 |____/ \___| .__/|_|\__, |
            |_|      |___/[/bold cyan]
 [dim]A modern dependency analysis CLI[/dim]
"""