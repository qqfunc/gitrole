"""Switch between Git configurations based on role."""

__all__ = ["main"]

import sys
from argparse import ArgumentParser
from collections.abc import Sequence

from . import GitRole


class Arguments:
    """A class for GitRole CLI arguments."""

    role: str
    config: str | None
    global_: bool


def main(args: Sequence[str] | None = None) -> None:
    """Run the GitRole CLI."""
    parser = ArgumentParser(
        prog="gitrole",
        description="Switch between Git configurations based on role.",
    )
    parser.add_argument("role", help="The role to switch to.")
    parser.add_argument(
        "-c",
        "--config",
        help="Path to the configuration file.",
    )
    parser.add_argument(
        "-g",
        "--global",
        action="store_true",
        help="Use global Git configuration.",
        dest="global_",
    )

    parsed_args = parser.parse_args(args, Arguments())

    try:
        GitRole(parsed_args.role, parsed_args.config, global_=parsed_args.global_)
    except (IsADirectoryError, FileNotFoundError, ValueError, KeyError) as e:
        sys.exit(e)
