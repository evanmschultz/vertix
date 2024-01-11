import pytest
from unittest.mock import Mock, patch
from vertix.db import ChromaDBHandler
from vertix.typings import PrimitiveType


@pytest.fixture
def mock_client() -> Mock:
    """Return a mock ChromaDB client."""
    client = Mock()
    return client


@pytest.fixture
def chroma_db_handler(mock_client: Mock) -> ChromaDBHandler:
    """Return a ChromaDBHandler instance."""
    return ChromaDBHandler(mock_client)


def test_chroma_db_handler_initialization(mock_client: Mock) -> None:
    """Test that the ChromaDBHandler instance is initialized correctly."""
    handler = ChromaDBHandler(mock_client)
    assert handler.client is mock_client


@patch("vertix.utilities.utilities.all_are_strings", return_value=True)
def test_get_or_create_collection(
    mock_all_are_strings, chroma_db_handler: ChromaDBHandler
) -> None:
    """Test that a collection is created with the correct data."""
    collection_name = "test_collection"
    collection_metadata: dict[str, PrimitiveType] = {"example": "metadata"}
    embedding_function = Mock()

    with patch.object(
        chroma_db_handler.client, "get_or_create_collection", return_value=Mock()
    ) as mock_method:
        chroma_db_handler.get_or_create_collection(
            collection_name, collection_metadata, embedding_function
        )
        mock_method.assert_called_once_with(
            name=collection_name,
            metadata=collection_metadata,
            embedding_function=embedding_function,
        )


@pytest.mark.parametrize(
    "collection_name, collection_metadata",
    [
        (123, {"example": "metadata"}),
        ("test_collection", 123),
        ("test_collection", []),
        ({}, {"example": 123}),
        ("test_collection", ()),
        ("test_collection", 1.2),
        ("test_collection", True),
        (None, {"example": "metadata"}),
        {True, "metadata"},
        (1.2, "metadata"),
    ],
)
def test_get_or_create_collection_type_error(
    collection_name: str,
    collection_metadata: dict[str, PrimitiveType],
    chroma_db_handler: ChromaDBHandler,
) -> None:
    """Test that a TypeError is raised if the collection name or metadata are not strings."""
    with pytest.raises(TypeError):
        chroma_db_handler.get_or_create_collection(
            name=collection_name,
            metadata=collection_metadata,
        )


def test_delete_collection(chroma_db_handler: ChromaDBHandler) -> None:
    """Test that a collection is deleted with the correct data."""
    collection_name = "test_collection"
    with patch.object(chroma_db_handler.client, "delete_collection") as mock_method:
        chroma_db_handler.delete_collection(collection_name)
        mock_method.assert_called_once_with(name=collection_name)


@pytest.mark.parametrize("collection_name", [123, [], {}, (), 1.2, True, None])
def test_delete_collection_type_error(
    collection_name: str, chroma_db_handler: ChromaDBHandler
) -> None:
    """Test that a TypeError is raised if the collection name is not a string."""
    with pytest.raises(TypeError):
        chroma_db_handler.delete_collection(name=collection_name)


def test_reset_client(chroma_db_handler: ChromaDBHandler) -> None:
    """Test that the client is reset."""
    with patch.object(
        chroma_db_handler.client, "reset", return_value=True
    ) as mock_reset:
        chroma_db_handler.reset_client()
        mock_reset.assert_called_once()


def test_reset_client_reset_exception(chroma_db_handler: ChromaDBHandler) -> None:
    """Test that an Exception is raised if the client could not be reset."""
    with patch.object(
        chroma_db_handler.client, "reset", side_effect=Exception("Test Exception")
    ) as mock_reset:
        with pytest.raises(Exception) as excinfo:
            chroma_db_handler.reset_client()
        assert "Test Exception" in str(excinfo.value)
