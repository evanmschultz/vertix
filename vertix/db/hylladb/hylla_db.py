import multiprocessing
from pathlib import Path
import shelve
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Any

from pydantic import BaseModel, Field, field_validator

import vertix.db.hylladb.hylla_utilities as hylla_utils

# BokKās or BokHylla or BokSkåp, or Skåp, Kās, or Hylla


class HyllaDB(BaseModel):
    """
    Remove Pydantic, should use no dependencies
    """

    library_path_str: str = Field(
        default="./test_db", description="The base directory for the database files."
    )
    section_path_strs: list[str] | None = None

    def __post_init__(self) -> None:
        self.library_path = Path(self.library_path_str)
        self.library_path.mkdir(parents=True, exist_ok=True)
        self.shelf_locks: dict = {}  # Dictionary to store locks for each shelf
        self.executor = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())
        self.paths: set[Path] = set()

        if self.section_path_strs:
            for section in self.section_path_strs:
                self.create_section(section)

    def _get_shelf_lock(self, shelf_path: Path) -> Lock:
        if shelf_path not in self.shelf_locks:
            self.shelf_locks[shelf_path] = Lock()
        return self.shelf_locks[shelf_path]

    def create_section(self, section_path: str, metadata: dict[str, Any] = {}) -> None:
        """
        Notes:
            - `section_path` is a relative path from the library path and should be noted using `.` between parent and child section names.
                - e.g. `section_path = "parent_section.new_section"`
        """
        if not isinstance(metadata, dict):
            raise TypeError(
                f"`metadata` argument must be a dictionary. Got type {type(metadata)} instead."
            )

        section_path = hylla_utils.get_validated_path_str(section_path)
        resolved_section_path: Path = self.library_path / section_path

        if resolved_section_path in self.paths or resolved_section_path.exists():
            # QUESTION: How should this be handled if the path exists but is not in `self.paths`?
            # That would mean that the path was created outside of the HyllaDB class.
            raise ValueError(f"Section '{section_path}' already exists.")

        resolved_section_path.mkdir()
        self.paths.add(resolved_section_path)

        metadata_path: Path = resolved_section_path / "metadata.db"
        metadata_lock: Lock = self._get_shelf_lock(metadata_path)
        with metadata_lock:
            with shelve.open(str(metadata_path)) as shelf:
                shelf.clear()
                shelf.update(**metadata)

    def checkout_section(self, section_path: str) -> dict[str, dict[str, Any]]:
        """
        Notes:
            - `section_path` is a relative path from the library path and should be noted using `.` between parent and child section names.
                - e.g. `section_path = "parent_section.target_section"`
        """

        resolved_section_path: Path = hylla_utils.resolved_section_path(
            section_path, self.library_path
        )
        if (
            resolved_section_path not in self.paths
            or not resolved_section_path.exists()
        ):
            # QUESTION: How should this be handled if the path exists but is not in `self.paths`?
            # That would mean that the path was created outside of the HyllaDB class.
            raise ValueError(f"Section '{section_path}' not found.")

        # shelves_data: dict[str, dict[str, Any]] = {}
        # for shelf_path in resolved_section_path.glob("**/*.db"):
        #     shelves_data[shelf_path.stem] = self.checkout_shelf(str(shelf_path))

        # return shelves_data
        return self._build_nested_dict(resolved_section_path)

    def rewrite_section_name(self, new_name: str, section_path: str) -> None:
        """
        Args:
            - `new_name`: The new name for the section.
            - `section_path`: The path to the section to be renamed, must include the old name of the section.
                - e.g. `section_path = "parent_section.old_name"`

        Notes:
            - `section_path` is a relative path from the library path and should be noted using `.` between parent and child section names.
                - e.g. `section_path = "parent_section.old_name"`
        """
        resolved_section_path: Path = hylla_utils.resolved_section_path(
            section_path, self.library_path
        )
        if (
            resolved_section_path not in self.paths
            or not resolved_section_path.exists()
        ):
            # QUESTION: How should this be handled if the path exists but is not in `self.paths`?
            # That would mean that the path was created outside of the HyllaDB class.
            raise ValueError(f"Section '{section_path}' not found.")

        new_section_path: Path = self.library_path / new_name
        resolved_section_path.rename(new_section_path)
        self.paths.remove(resolved_section_path)
        self.paths.add(new_section_path)

        for path in self.paths:
            if path.parent == resolved_section_path:
                new_sub_path: Path = new_section_path / path.name
                path.rename(new_sub_path)
                self.paths.remove(path)
                self.paths.add(new_sub_path)

    def rewrite_section_metadata(
        self, section_path: str, metadata: dict[str, Any]
    ) -> None:
        """
        Notes:
            - `section_path` is a relative path from the library path and should be noted using `.` between parent and child section names.
                - e.g. `section_path = "parent_section.target_section"`
        """
        if not isinstance(metadata, dict):
            raise TypeError(
                f"`metadata` argument must be a dictionary. Got type {type(metadata)} instead."
            )

        resolved_section_path: Path = hylla_utils.resolved_section_path(
            section_path, self.library_path
        )
        if (
            resolved_section_path not in self.paths
            or not resolved_section_path.exists()
        ):
            raise ValueError(f"Section '{section_path}' not found.")

        metadata_path: Path = resolved_section_path / "metadata.db"
        metadata_lock: Lock = self._get_shelf_lock(metadata_path)
        with metadata_lock:
            with shelve.open(str(metadata_path), writeback=True) as shelf:
                shelf.clear()
                shelf.update(**metadata)

    def remove_section(self, section_path: str) -> None:
        """
        Notes:
            - `section_path` is a relative path from the library path and should be noted using `.` between parent and child section names.
                - e.g. `section_path = "parent_section.target_section"`
        """
        resolved_section_path: Path = hylla_utils.resolved_section_path(
            section_path, self.library_path
        )
        if (
            resolved_section_path not in self.paths
            or not resolved_section_path.exists()
        ):
            raise ValueError(
                f"Section '{section_path}' not found and thus cannot be removed."
            )

        resolved_section_path.rmdir()
        self.paths.remove(resolved_section_path)

    def clear_section(self, section_path: str) -> None:
        """
        Notes:
            - `section_path` is a relative path from the library path and should be noted using `.` between parent and child section names.
                - e.g. `section_path = "parent_section.target_section"`
        """
        resolved_section_path: Path = hylla_utils.resolved_section_path(
            section_path, self.library_path
        )
        if (
            resolved_section_path not in self.paths
            or not resolved_section_path.exists()
        ):
            raise ValueError(
                f"Section '{section_path}' not found and thus cannot be clear."
            )

        # remove all shelves in the section
        for shelf_path in resolved_section_path.glob("**/*.db"):
            shelf_path.unlink()

    def create_shelf(
        self,
        shelf_name: str,
        path: str | None = None,
        metadata: dict[str, Any] = {},
    ) -> None:
        """If `path` is not specified, the shelf will be created in the library path (the root directory of the database)."""
        if shelf_name == "metadata":
            raise ValueError("The shelf name 'metadata' is a reserved name in HyllaDB.")

        if not path:
            resolved_section_path = self.library_path
        else:
            resolved_section_path: Path = hylla_utils.resolved_section_path(
                path, self.library_path
            )

        shelf_path: Path = resolved_section_path / f"{shelf_name}.db"
        # if shelf_path.exists():
        #     raise ValueError(f"Shelf '{shelf_name}' already exists in {resolved_path}.")
        if shelf_path in self.paths or shelf_path.exists():
            raise KeyError(f"Shelf '{shelf_name}' already exists in {path}.")
        self.paths.add(shelf_path)

        lock: Lock = self._get_shelf_lock(shelf_path)
        with lock:
            with shelve.open(str(shelf_path)) as shelf:
                shelf.update(**metadata)

    def checkout_shelf(self, shelf_path: str) -> dict[str, Any]:
        resolved_path: Path = hylla_utils.get_shelf_path(shelf_path, self.library_path)

        if not resolved_path.exists() or resolved_path not in self.paths:
            raise KeyError(f"Shelf '{shelf_path}' does not exist.")

        lock: Lock = self._get_shelf_lock(resolved_path)
        with lock:
            with shelve.open(str(resolved_path), writeback=True) as shelf:
                return dict(shelf)

    def rewrite_shelf_metadata(self, shelf_path: str, metadata: dict[str, Any]) -> None:
        resolved_path: Path = hylla_utils.get_shelf_path(shelf_path, self.library_path)

        if not resolved_path.exists() or resolved_path not in self.paths:
            raise KeyError(f"Shelf '{shelf_path}' does not exist.")

        lock: Lock = self._get_shelf_lock(resolved_path)
        with lock:
            with shelve.open(str(resolved_path), writeback=True) as shelf:
                shelf["metadata"] = metadata

    def rewrite_shelf_name(self, new_name: str, shelf_path: str) -> None:
        resolved_path: Path = hylla_utils.get_shelf_path(shelf_path, self.library_path)

        if not resolved_path.exists() or resolved_path not in self.paths:
            raise KeyError(f"Shelf '{shelf_path}' does not exist.")

        new_shelf_path: Path = resolved_path.parent / f"{new_name}.db"
        resolved_path.rename(new_shelf_path)
        self.paths.remove(resolved_path)
        self.paths.add(new_shelf_path)

    def remove_shelf(self, shelf_path: str) -> None:
        resolved_path: Path = hylla_utils.get_shelf_path(shelf_path, self.library_path)

        if not resolved_path.exists():
            raise ValueError(f"Shelf '{shelf_path}' does not exist.")

        self.paths.remove(resolved_path)
        resolved_path.unlink()  # remove the file

    def clear_shelf(self, shelf_path: str) -> None:
        """Clear all data from the shelf keeping the shelf in place."""
        resolved_path: Path = hylla_utils.get_shelf_path(shelf_path, self.library_path)

        lock: Lock = self._get_shelf_lock(resolved_path)
        with lock:
            with shelve.open(str(shelf_path), writeback=True) as shelf:
                shelf.clear()

    def checkout_library(self) -> dict[str, dict[str, Any]]:
        # all_data: dict[str, Any] = {}
        # for shelf_path in self.library_path.glob("**/*.db"):
        #     all_data[shelf_path.stem] = self.checkout_shelf(str(shelf_path))

        # return all_data
        return self._build_nested_dict(self.library_path)

    def _build_nested_dict(self, current_path: Path) -> dict[str, Any]:
        if current_path.is_file() and current_path.suffix == ".db":
            # For files, return the data from the shelf
            return self.checkout_shelf(str(current_path))
        elif current_path.is_dir():
            # For directories, recursively build the nested structure
            nested_dict: dict[str, Any] = {}
            for child in current_path.iterdir():
                nested_dict[child.stem] = self._build_nested_dict(child)
            return nested_dict
        else:
            # Handle non-directory and non-db file cases if needed
            return {}

    @field_validator("library_path_str")
    def _validate_library_path_str(cls, v: str) -> str:
        try:
            Path(v).resolve()
        except Exception:
            raise ValueError(f"Invalid path format: {v}")
        return v

    # def write_to_shelf(self, shelf_name: str, path: list[str], value: Any) -> None:
    #     if not path:
    #         raise ValueError("The `path` argument cannot be an empty list.")

    #     lock: Lock = self._get_shelf_lock(shelf_name)
    #     base_key: str = path[0]
    #     nested_keys: list[str] = path[1:]
    #     shelf_path: Path = shelf_utils.get_shelf_path(shelf_name, self.library_path)

    #     with lock:
    #         with shelve.open(str(shelf_path), writeback=True) as shelf:
    #             if base_key in shelf:
    #                 # Retrieve existing dictionary
    #                 existing_value = shelf[base_key]
    #             else:
    #                 # If the base key does not exist, create a new nested structure
    #                 existing_value: dict[str, Any] = {}

    #             # Navigate to the nested key and rewrite
    #             current_element: dict[str, Any] = existing_value
    #             for key in nested_keys[:-1]:
    #                 current_element = current_element.setdefault(key, {})

    #             current_element[nested_keys[-1]] = value

    #             # rewrite the shelve database
    #             shelf[base_key] = existing_value
    #             shelf.sync()

    # def navigate_to_nested_key(
    #     self, dictionary: dict[str, Any], path: list[str]
    # ) -> tuple[dict[str, Any], str]:
    #     """Navigate to the nested key based on the path."""

    #     current_element: dict[str, Any] = dictionary
    #     for key in path[:-1]:  # Navigate to the parent of the target key
    #         if key not in current_element:
    #             raise KeyError(f"Key '{key}' not found in the nested dictionary.")
    #         current_element = current_element[key]

    #     last_key: str = path[-1]
    #     if last_key not in current_element:
    #         raise KeyError(f"Key '{last_key}' not found in the nested dictionary.")

    #     return current_element, last_key

    # def get_nested_value(self, dictionary: dict[str, Any], path: list[str]) -> Any:
    #     """Retrieve a value from a nested dictionary."""
    #     if not isinstance(dictionary, dict):
    #         raise TypeError(
    #             f"`db` argument must be a dictionary. Got type {type(dictionary)} instead."
    #         )
    #     if (
    #         not isinstance(path, list)
    #         or not all(isinstance(key, str) for key in path)
    #         or not path
    #     ):
    #         raise TypeError(
    #             f"`path` argument must be a non-empty list of strings. Got type {type(path)}"
    #         )

    #     parent_dict, last_key = self.navigate_to_nested_key(dictionary, path)
    #     return parent_dict[last_key]

    # def rewrite_nested_value(
    #     self, shelf_name: str, path: list[str], value: Any
    # ) -> None:
    #     if (
    #         not isinstance(path, list)
    #         or not all(isinstance(key, str) for key in path)
    #         or not path
    #     ):
    #         raise TypeError(
    #             f"`path` argument must be a non-empty list of strings. Got type {type(path)}"
    #         )

    #     lock: Lock = self._get_shelf_lock(shelf_name)
    #     shelf_path: Path = shelf_utils.get_shelf_path(shelf_name, self.library_path)
    #     with lock:
    #         with shelve.open(str(shelf_path), writeback=True) as shelf:
    #             parent_dict, last_key = self.navigate_to_nested_key(dict(shelf), path)
    #             parent_dict[last_key] = value
    #             # No need to return the dictionary, as changes are made in place

    # @field_validator("sections_path_strs")
    # def _validate_sections_directory_strs(cls, v: list[str]) -> list[str]:
    #     for section in v:
    #         try:
    #             Path(section).resolve()
    #         except Exception:
    #             raise ValueError(f"Invalid path format: {section}")
    #     return v


# hylla = HyllaDB()

# def write_to_db(self, db_file: str, path: list[str], value: Any) -> None:
#     if not path:
#         raise ValueError("The `path` argument cannot be an empty list.")

#     base_key: str = path[0]
#     nested_keys: list[str] = path[1:]

#     with self.db_lock:
#         with shelve.open(db_file, writeback=True) as db:
#             if base_key in db:
#                 # Retrieve existing dictionary
#                 existing_value = db[base_key]
#             else:
#                 # If the base key does not exist, create a new nested structure
#                 existing_value: dict[str, Any] = {}

#             # Navigate to the nested key and rewrite
#             current_element: dict[str, Any] = existing_value
#             for key in nested_keys[:-1]:
#                 current_element = current_element.setdefault(key, {})

#             current_element[nested_keys[-1]] = value

#             # rewrite the shelve database
#             db[base_key] = existing_value
#             db.sync()

# def rewrite_nested_value(self, db, path: list[str], value: Any) -> dict[str, Any]:
#     """Set a value in a nested dictionary."""
#     if (
#         not isinstance(path, list)
#         or not all(isinstance(key, str) for key in path)
#         or not path
#     ):
#         raise TypeError(
#             f"`path` argument must be a non-empty list of strings. Got type {type(path)}"
#         )

#     parent_dict, last_key = self.navigate_to_nested_key(db, path)
#     parent_dict[last_key] = value
#     return parent_dict


# @app.get("/{shelf_name}/items/{path:path}")
# async def read(shelf_name: str, path: list[str]) -> Any:
#     db: dict[str, Any] = get_shelf_data(shelf_name)
#     return get_nested_value(db, path)


# @app.put("/{shelf_name}/items/{path:path}")
# async def write(shelf_name: str, path: list[str], value: Any) -> dict[str, str]:
#     try:
#         db_path = get_shelf_path(shelf_name)
#         write_to_db(str(db_path), path, value)
#     except (KeyError, ValueError, TypeError) as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     return {"message": "Item rewrited successfully"}


# vrtx_db = VertixDB()
# Modify the other helper functions

# @app.get("/items/{path:path}")
# async def read(path: list[str]) -> Any:
#     db: dict[str, Any] = get_db()
#     return get_nested_value(db, path)


# @app.put("/items/{path:path}")
# async def write(path: list[str], value: Any) -> dict[str, str]:
#     try:
#         write_to_db(db_file, path, value)
#     except (KeyError, ValueError, TypeError) as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     return {"message": "Item rewrited successfully"}
