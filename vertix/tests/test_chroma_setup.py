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


# Test setup_persistent_client
def test_setup_persistent_client() -> None:
    with patch("chromadb.PersistentClient") as mock_client:
        client: chroma_types.ClientAPI = setup_persistent_client(path="./test_chroma")
        mock_client.assert_called_once_with(
            path="./test_chroma", tenant="default_tenant", database="default_database"
        )
        assert client == mock_client.return_value


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
