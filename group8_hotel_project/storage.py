"""JSON file handling and exception management (CO4)."""

import json
from pathlib import Path
from typing import Any


class StorageError(Exception):
    """Raised when reading or writing a JSON file fails."""


class JsonStorage:
    """Handles reading and writing JSON files safely with try/except blocks."""

    def __init__(self, data_directory: str | Path) -> None:
        self.data_directory = Path(data_directory)
        try:
            self.data_directory.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise StorageError(f"Cannot create data directory: {exc}") from exc

    def path_for(self, filename: str) -> Path:
        if Path(filename).name != filename:
            raise StorageError("Invalid data filename.")
        return self.data_directory / filename

    def read_json(self, filename: str, default: Any) -> Any:
        path = self.path_for(filename)
        if not path.exists():
            return default
        try:
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as exc:
            raise StorageError(f"{filename} contains invalid JSON: {exc}") from exc
        except OSError as exc:
            raise StorageError(f"Could not read {filename}: {exc}") from exc

    def write_json(self, filename: str, data: Any) -> None:
        path = self.path_for(filename)
        try:
            with path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
                file.write("\n")
        except (OSError, TypeError, ValueError) as exc:
            raise StorageError(f"Could not save {filename}: {exc}") from exc
