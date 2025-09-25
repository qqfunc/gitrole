"""Switch between Git configurations based on role."""

from __future__ import annotations

import json
import os
import tomllib
from os import PathLike
from pathlib import Path
from typing import Any

CONFIG_FILE_EXTENSIONS = [
    "toml",
    "json",
]


def get_config_path() -> Path | None:
    """Get the GitRole configuration paths."""
    # Get config directory path
    # XDG Base Directory: https://wiki.archlinux.org/title/XDG_Base_Directory
    xdg_config_home = Path(
        os.getenv("XDG_CONFIG_HOME", "~/.config"),
    ).expanduser()

    # Check for XDG_CONFIG_HOME environment variable
    config_paths = [
        xdg_config_home.joinpath(f"gitrole.{ext}")
        for ext in CONFIG_FILE_EXTENSIONS
    ]

    for config_path in config_paths:
        if config_path.is_file():
            return config_path

    return None


def get_config(path: str | PathLike | None) -> dict[str, Any] | None:
    """Get the GitRole configuration."""
    path = get_config_path() if path is None else Path(path)

    if path is None:
        return None

    match path.suffix:
        case "toml":
            with path.open("rb") as f:
                return tomllib.load(f)
        case "json":
            with path.open() as f:
                return json.load(f)

    return None

class Config:
    """GitRole configuration."""
