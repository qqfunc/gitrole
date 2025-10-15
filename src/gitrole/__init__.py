"""Switch between Git configurations based on role."""

from __future__ import annotations

__all__ = ["GitRole"]

import json
import os
import tomllib
from enum import StrEnum
from os import PathLike
from pathlib import Path
from typing import Any

import pygit2
import yaml
from filelock import FileLock


class ConfigFileExtension(StrEnum):
    """Supported configuration file extensions."""

    TOML = "toml"
    JSON = "json"
    YML = "yml"
    YAML = "yaml"


class GitRole:
    """A class for managing Git configurations based on role."""

    def __init__(
        self,
        role: str,
        config_path: str | PathLike | None = None,
        *,
        global_: bool = False,
    ) -> None:
        """Initialize self."""
        self.role = role

        if config_path is None:
            self.config_path = self.get_config_path()
        else:
            self.config_path = Path(config_path)
            if not self.config_path.is_file():
                if self.config_path.is_dir():
                    msg = f"{self.config_path} is a directory"
                    raise IsADirectoryError(msg)
                msg = f"Configuration file '{self.config_path}' not found"
                raise FileNotFoundError(msg)

        self.git_config = (
            pygit2.Config.get_global_config()
            if global_
            else pygit2.Repository(".").config
        )

        with FileLock(self.lock_path):
            try:
                self.previous_role = self.git_config["gitrole.role"]
            except KeyError:
                self.previous_role = None

            self.config = self.get_config()
            self.reset_previous_role()
            self.apply_role()

    @property
    def xdg_config_home(self) -> Path:
        """Get the XDG Config Home directory.

        XDG Base Directory: https://wiki.archlinux.org/title/XDG_Base_Directory
        """
        return Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser()

    def get_config_path(self) -> Path:
        """Get the GitRole configuration path."""
        config_paths = [
            self.xdg_config_home / f"gitrole/gitrole.{ext}"
            for ext in ConfigFileExtension
        ]

        for config_path in config_paths:
            if config_path.is_file():
                return config_path

        msg = "No configuration file found."
        raise FileNotFoundError(msg)

    @property
    def lock_path(self) -> Path:
        """Get the GitRole lock file path."""
        return self.xdg_config_home / "gitrole/gitrole.lock"

    def get_config(self) -> dict[str, Any]:
        """Get the GitRole configuration."""
        try:
            extension = ConfigFileExtension(
                self.config_path.suffix.lstrip("."),
            )
        except ValueError:
            msg = (
                "Unsupported configuration file format "
                f"'{self.config_path.suffix}'."
            )
            raise ValueError(msg) from None
        match extension:
            case ConfigFileExtension.TOML:
                with self.config_path.open("rb") as f:
                    return tomllib.load(f)
            case ConfigFileExtension.JSON:
                with self.config_path.open("rb") as f:
                    return json.load(f)
            case ConfigFileExtension.YML | ConfigFileExtension.YAML:
                with self.config_path.open("rb") as f:
                    return yaml.safe_load(f)

    def reset_previous_role(self) -> None:
        """Reset to the previous Git configuration."""
        if (
            self.previous_role is None
            or (config := self.config.get(self.previous_role)) is None
            or not isinstance(config, dict)
        ):
            return

        for key in config:
            del self.git_config[key]

    def apply_role(self) -> None:
        """Apply the Git configuration for the specified role."""
        if (config := self.config.get(self.role)) is None:
            msg = (
                f"Role '{self.role}' not found in configuration file "
                f"{self.config_path}."
            )
            raise KeyError(msg)

        if not isinstance(config, dict):
            msg = f"Invalid configuration for role '{self.role}'."
            raise TypeError(msg)

        for key, value in config.items():
            if not isinstance(value, str):
                msg = f"Invalid value for '{key}' in role '{self.role}'."
                raise TypeError(msg)
            self.git_config[key] = value

        self.git_config["gitrole.role"] = self.role
