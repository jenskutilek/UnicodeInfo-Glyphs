from __future__ import annotations

import codecs
import json
import os

from pathlib import Path
from typing import Any

base_path = Path(os.path.split(Path(__file__).resolve().parent)[0])
json_path = base_path / "json"


def json_to_file(
    path: Path, file_name: str, obj: Any, human_readable: bool = True
) -> None:
    with codecs.open(str(path / f"{file_name}.json"), "w", "utf-8") as f:
        if human_readable:
            indent = 4
        else:
            indent = None
        json.dump(obj, f, ensure_ascii=False, indent=indent, sort_keys=True)


def dict_from_file(path: Path, file_name: str) -> Any:
    with codecs.open(str(path / f"{file_name}.json"), "r", "utf-8") as f:
        return json.load(f)


def clean_json_dir(path: Path):
    # Clean up the directory which contains the separate json files to avoid
    # orphaned files
    for file_path in path.iterdir():
        name = str(file_path)
        if not name[0] == "." and name.lower().endswith(".json"):
            try:
                (path / name).unlink()
            except FileNotFoundError:
                print(
                    "WARNING: Could not remove file before regenerating it:",
                    os.path.join(path, name),
                )
