import shutil
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from vertix.db import setup_client
from vertix.typings import chroma_types


# Tests for setup_ephemeral_client
def test_setup_ephemeral_client_returns_correct_type() -> None:
    client: chroma_types.ClientAPI = setup_client.setup_ephemeral_client()
    assert isinstance(client, chroma_types.ClientAPI)


# Fixture for creating and tearing down a persistent client
@pytest.fixture
def persistent_client() -> Generator[str, None, None]:
    path = "./test_chroma_db_temp"
    yield path

    # Teardown directory
    shutil.rmtree(path)


# Tests for setup_persistent_client
def test_setup_persistent_client_returns_correct_type(persistent_client: str) -> None:
    client: chroma_types.ClientAPI = setup_client.setup_persistent_client(
        persistent_client
    )
    assert isinstance(client, chroma_types.ClientAPI)


# Tests for setup_http_client
@patch("chromadb.HttpClient")
def test_setup_http_client_returns_correct_type(mocked_http_client) -> None:
    mocked_http_client.return_value = MagicMock(spec=chroma_types.ClientAPI)
    client: chroma_types.ClientAPI = setup_client.setup_http_client()
    assert isinstance(client, chroma_types.ClientAPI)


# Test exception handling for setup_ephemeral_client
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
    with pytest.raises(TypeError):
        setup_client.setup_ephemeral_client(tenant, database)


# Test exception handling for setup_persistent_client
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
    with pytest.raises(TypeError):
        setup_client.setup_persistent_client(path, tenant, database)


# Test exception handling for setup_http_client
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
    with pytest.raises(TypeError):
        setup_client.setup_http_client(host, port, ssl, headers)
