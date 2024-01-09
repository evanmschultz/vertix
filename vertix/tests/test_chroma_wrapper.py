import pytest
from unittest.mock import Mock, patch
from vertix.models import Node
from vertix.db.chroma_wrapper import ChromaDBWrapper


# Fixture for the ChromaDBWrapper instance
@pytest.fixture
def chroma_db_wrapper() -> ChromaDBWrapper:
    client_api_mock = Mock()
    collection_mock = Mock()
    client_api_mock.get_or_create_collection.return_value = collection_mock
    return ChromaDBWrapper(client_api_mock, "test_collection")


# Fixture for a mock Node
@pytest.fixture
def mock_node() -> Mock:
    node = Mock()
    node.id = "12345678-1234-5678-1234-567812345678"
    node.label = "Test Label"
    node.document = "Test Document"
    node.description = "Test Description"
    node.type = "Test Type"
    node.neighbors_count = 0
    node.created_at = "2024-01-01T00:00:00"
    node.updated_at = "2024-01-01T00:00:00"
    node.additional_attributes = {"example": "example"}
    node.serialize.return_value = {
        "id": node.id,
        "label": node.label,
        "document": node.document,
        "description": node.description,
        "type": node.type,
        "neighbors_count": node.neighbors_count,
        "created_at": node.created_at,
        "updated_at": node.updated_at,
        **node.additional_attributes,
    }
    return node


# Test for adding a node
def test_add_node(chroma_db_wrapper: ChromaDBWrapper, mock_node: Mock) -> None:
    chroma_db_wrapper.add_node(mock_node)

    # Check if the node was added to the collection with correct data
    expected_data = mock_node.serialize()
    chroma_db_wrapper.collection.add.assert_called_with(
        ids=mock_node.id, documents="Test Document", metadatas=expected_data
    )


# Test for correct initialization
def test_chroma_db_wrapper_initialization(chroma_db_wrapper: ChromaDBWrapper) -> None:
    assert chroma_db_wrapper.collection is not None
    assert chroma_db_wrapper.chroma_client is not None


# Test error handling in add_node
@patch("vertix.models.Node")
def test_add_node_error_handling(
    node_mock: Mock, chroma_db_wrapper: ChromaDBWrapper
) -> None:
    node_mock.id = "test_id"
    node_mock.serialize.side_effect = Exception("Test Exception")

    with pytest.raises(Exception) as excinfo:
        chroma_db_wrapper.add_node(node_mock)

    assert "Test Exception" in str(excinfo.value)
