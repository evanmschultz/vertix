from pathlib import Path


def resolved_section_path(section_path: str, library_path: Path) -> Path:
    section_path = get_validated_path_str(section_path)
    resolved_path: Path = library_path / section_path
    if not resolved_path.exists():
        raise ValueError(f"Case '{section_path}' not found.")
    return resolved_path


def get_shelf_path(shelf_path: str, library_path: Path) -> Path:
    shelf_path = get_validated_path_str(shelf_path)
    resolved_path: Path = library_path / shelf_path
    if not resolved_path.exists():
        raise ValueError(f"Shelf '{shelf_path}' not found.")
    return resolved_path


def get_validated_path_str(path: str) -> str:
    try:
        path_str: str = path.replace(".", "/")
        Path(path_str).resolve()
        return path_str
    except Exception as e:
        raise ValueError(
            f"Invalid path format: {path}. Expected format: `parent.target`"
        ) from e
