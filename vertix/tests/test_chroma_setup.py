import pytest
from unittest.mock import patch
import chromadb

from vertix.typings import chroma_types
from vertix.db.chroma_setup import (
    setup_ephemeral_client,
    setup_persistent_client,
    set_up_http_client,
)


# Test setup_ephemeral_client
def test_setup_ephemeral_client() -> None:
    with patch("chromadb.EphemeralClient") as mock_client:
        client: chroma_types.ClientAPI = setup_ephemeral_client()
        mock_client.assert_called_once_with(
            tenant="default_tenant", database="default_database"
        )
        assert client == mock_client.return_value


# Test setup_ephemeral_client with custom tenant and database
def test_setup_ephemeral_client_custom_tenant_and_database() -> None:
    with patch("chromadb.EphemeralClient") as mock_client:
        client: chroma_types.ClientAPI = setup_ephemeral_client(
            tenant="test_tenant", database="test_database"
        )
        mock_client.assert_called_once_with(
            tenant="test_tenant", database="test_database"
        )
        assert client == mock_client.return_value


# Test setup_ephemeral_client with invalid tenant and database
def test_setup_ephemeral_client_invalid_tenant_and_database() -> None:
    with pytest.raises(TypeError):
        setup_ephemeral_client(tenant=1, database=2)  # type: ignore # tenant and database invalid type
    with pytest.raises(TypeError):
        setup_ephemeral_client(tenant=1, database="test_database")  # type: ignore # tenant invalid type
    with pytest.raises(TypeError):
        setup_ephemeral_client(tenant="test_tenant", database=2)  # type: ignore # database invalid type


# Test setup_persistent_client
def test_setup_persistent_client() -> None:
    with patch("chromadb.PersistentClient") as mock_client:
        client: chroma_types.ClientAPI = setup_persistent_client(path="./test_chroma")
        mock_client.assert_called_once_with(
            path="./test_chroma", tenant="default_tenant", database="default_database"
        )
        assert client == mock_client.return_value


# Test setup_persistent_client with custom args
def test_setup_persistent_client_custom_args() -> None:
    with patch("chromadb.PersistentClient") as mock_client:
        client: chroma_types.ClientAPI = setup_persistent_client(
            path="./test_chroma", tenant="test_tenant", database="test_database"
        )
        mock_client.assert_called_once_with(
            path="./test_chroma", tenant="test_tenant", database="test_database"
        )
        assert client == mock_client.return_value


# Test setup_persistent_client with invalid args
def test_setup_persistent_client_invalid_args() -> None:
    with pytest.raises(TypeError):
        setup_persistent_client(path=1, tenant=2, database=3)  # type: ignore # path, tenant, and database invalid type
    with pytest.raises(TypeError):
        setup_persistent_client(path=1, tenant="test_tenant", database="test_database")  # type: ignore # path invalid type
    with pytest.raises(TypeError):
        setup_persistent_client(path="./test_chroma", tenant=1, database="test_database")  # type: ignore # tenant invalid type
    with pytest.raises(TypeError):
        setup_persistent_client(path="./test_chroma", tenant="test_tenant", database=1)  # type: ignore # database invalid type


# Test set_up_http_client
def test_set_up_http_client() -> None:
    with patch("chromadb.HttpClient") as mock_client:
        client: chroma_types.ClientAPI = set_up_http_client(
            host="localhost", port="8000", ssl=False, headers={}
        )
        mock_client.assert_called_once_with(
            host="localhost", port="8000", ssl=False, headers={}
        )
        assert client == mock_client.return_value


# Test set_up_http_client with custom args
def test_set_up_http_client_custom_args() -> None:
    with patch("chromadb.HttpClient") as mock_client:
        client: chroma_types.ClientAPI = set_up_http_client(
            host="test_host",
            port="test_port",
            ssl=True,
            headers={"test_header": "test_value"},
        )
        mock_client.assert_called_once_with(
            host="test_host",
            port="test_port",
            ssl=True,
            headers={"test_header": "test_value"},
        )
        assert client == mock_client.return_value


# Test set_up_http_client with invalid args
def test_set_up_http_client_invalid_args() -> None:
    with pytest.raises(TypeError):
        set_up_http_client(host=1, port=2, ssl=3, headers=4)  # type: ignore # host, port, ssl, and headers invalid type
    with pytest.raises(TypeError):
        set_up_http_client(host=1, port="test_port", ssl=True, headers={"test_header": "test_value"})  # type: ignore # host invalid type
    with pytest.raises(TypeError):
        set_up_http_client(host="test_host", port=2, ssl=True, headers={"test_header": "test_value"})  # type: ignore # port invalid type
    with pytest.raises(TypeError):
        set_up_http_client(host="test_host", port="test_port", ssl=3, headers={"test_header": "test_value"})  # type: ignore # ssl invalid type
    with pytest.raises(TypeError):
        set_up_http_client(host="test_host", port="test_port", ssl=True, headers=4)  # type: ignore # headers invalid type
    with pytest.raises(TypeError):
        set_up_http_client(host="test_host", port="test_port", ssl=True, headers={"test_header": 4})  # type: ignore # headers (value) invalid type
    with pytest.raises(TypeError):
        set_up_http_client(host="test_host", port="test_port", ssl=True, headers={4: "test_value"})  # type: ignore # headers (key) invalid type
