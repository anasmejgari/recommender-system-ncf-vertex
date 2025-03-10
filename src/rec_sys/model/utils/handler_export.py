"""Module to handle export."""

import shutil
from pathlib import Path


def copy_handler_file(where_to_copy: Path) -> None:
    """Copy the handler file to new location.

    Args:
        where_to_copy (Path): Where to store the file.
    """
    handler_file = Path(__file__).parent.parent / "handler.py"
    shutil.copyfile(handler_file, where_to_copy)
