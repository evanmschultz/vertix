import shutil
from typing import Generator
from unittest.mock import create_autospec, patch

import pytest

from vertix.db import setup_client
import vertix.typings.chroma as chroma_types


def test_setup_ephemeral_client_returns_correct_type() -> None:
    """Test that setup_ephemeral_client returns the correct type."""
    client: chroma_types.ClientAPI = setup_client.setup_ephemeral_client()
    assert isinstance(client, chroma_types.ClientAPI)


@pytest.fixture
def persistent_client() -> Generator[str, None, None]:
    """
    Return a generator with a path string to a persistent client and tears down the client after
    testing is complete.
    """
    path = "./test_chroma_db_temp"
    yield path

    shutil.rmtree(path)


def test_setup_persistent_client_returns_correct_type(persistent_client: str) -> None:
    """Test that setup_persistent_client returns the correct type."""
    client: chroma_types.ClientAPI = setup_client.setup_persistent_client(
        persistent_client
    )
    assert isinstance(client, chroma_types.ClientAPI)


@patch("chromadb.HttpClient")
def test_setup_http_client_returns_correct_type(mocked_http_client) -> None:
    """Test that setup_http_client returns the correct type."""
    mocked_http_client.return_value = create_autospec(chroma_types.ClientAPI)
    client: chroma_types.ClientAPI = setup_client.setup_http_client()
    assert isinstance(client, chroma_types.ClientAPI)


@pytest.mark.parametrize(
    "tenant, database",
    [
        (123, "database"),
        ("tenant", 123),
        (1.2, "database"),
        ("tenant", 1.2),
        (True, "database"),
        ("tenant", True),
        ({"key": "value"}, "database"),
        ("tenant", {"key": "value"}),
        ((1, 2, 3), "database"),
        ("tenant", (1, 2, 3)),
    ],
)
def test_setup_ephemeral_client_type_error(tenant: str, database: str) -> None:
    """Test exception handling for setup_ephemeral_client."""
    with pytest.raises(TypeError):
        setup_client.setup_ephemeral_client(tenant, database)


@pytest.mark.parametrize(
    "path, tenant, database",
    [
        (123, "tenant", "database"),
        ("path", 123, "database"),
        ("path", "tenant", 123),
        (1.2, "tenant", "database"),
        ("path", 1.2, "database"),
        ("path", "tenant", 1.2),
        (True, "tenant", "database"),
        ("path", True, "database"),
        ("path", "tenant", True),
        ({"key": "value"}, "tenant", "database"),
        ("path", {"key": "value"}, "database"),
        ("path", "tenant", {"key": "value"}),
        ((1, 2, 3), "tenant", "database"),
        ("path", (1, 2, 3), "database"),
        ("path", "tenant", (1, 2, 3)),
    ],
)
def test_setup_persistent_client_type_error(
    path: str, tenant: str, database: str
) -> None:
    """Test exception handling for setup_persistent_client."""
    with pytest.raises(TypeError):
        setup_client.setup_persistent_client(path, tenant, database)


@pytest.mark.parametrize(
    "host, port, ssl, headers",
    [
        (123, "8000", False, {}),
        ("localhost", 8000, False, {}),
        ("localhost", "8000", "not_a_bool", {}),
        ("localhost", "8000", False, 123),
        ("localhost", "8000", False, {"key": 123}),
        ("localhost", "8000", False, {123: "value"}),
    ],
)
def test_setup_http_client_type_error(
    host: str, port: str, ssl: bool, headers: dict[str, str]
) -> None:
    """Test exception handling for setup_http_client."""
    with pytest.raises(TypeError):
        setup_client.setup_http_client(host, port, ssl, headers)
