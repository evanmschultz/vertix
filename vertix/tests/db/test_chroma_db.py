import pytest
from unittest.mock import MagicMock, Mock, patch
from vertix.db import ChromaDB
from vertix import Node, Edge
from vertix.typings import PrimitiveType


@pytest.fixture
def chroma_db() -> ChromaDB:
    """Return a ChromaDB instance."""
    client_mock = Mock()
    collection_mock = Mock()
    return ChromaDB(client_mock, collection_mock)


def test_chroma_db_initialization(chroma_db: ChromaDB) -> None:
    """Test that the ChromaDB instance is initialized correctly."""
    assert chroma_db.collection is not None
    assert chroma_db.chroma_client is not None


@pytest.fixture()
def mock_node() -> Mock:
    """Return a mock Node object."""
    node = MagicMock()
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


def test_add_node(chroma_db: ChromaDB, mock_node: Mock) -> None:
    """Test that a node is added to the collection with the correct data."""
    with patch.object(ChromaDB, "_validate_node_type", return_value=True):
        chroma_db.add_node(mock_node)

        expected_data = mock_node.serialize()
        chroma_db.collection.add.assert_called_with(
            ids=mock_node.id, documents="Test Document", metadatas=expected_data
        )


def test_add_node_error_handling(mock_node: Mock, chroma_db: ChromaDB) -> None:
    """Test that errors are handled correctly when adding a node."""
    mock_node.id = "test_id"
    mock_node.serialize.side_effect = Exception("Test Exception")

    with patch.object(ChromaDB, "_validate_node_type", return_value=True):
        with pytest.raises(Exception) as excinfo1:
            chroma_db.add_node(mock_node)
        assert "Test Exception" in str(excinfo1.value)

    with pytest.raises(TypeError) as excinfo2:
        chroma_db.add_node("test")  # type: ignore # wrong type

    assert "Expected node to be of type Node" in str(excinfo2.value)


def test_get_node_success(chroma_db: ChromaDB, mock_node: Mock) -> None:
    """Test that a node is returned when it exists."""
    mock_response: dict[str, list[PrimitiveType]] = {
        "metadatas": [mock_node.serialize()]
    }
    chroma_db.collection.get.return_value = mock_response

    result: Node | None = chroma_db.get_node(mock_node.id)

    assert result is not None
    assert result.id == mock_node.id
    chroma_db.collection.get.assert_called_with(mock_node.id)


def test_get_node_non_existent(chroma_db: ChromaDB) -> None:
    """Test that None is returned when a node does not exist."""
    chroma_db.collection.get.return_value = None

    result: Node | None = chroma_db.get_node("non_existent_id")
    assert result is None
    chroma_db.collection.get.assert_called_with("non_existent_id")


@pytest.fixture
def mock_edge() -> Mock:
    """Return a mock Edge object."""
    edge = Mock()
    edge.id = "12345678-1234-5678-1234-567812345678"
    edge.label = "Test Label"
    edge.document = "Test Document"
    edge.is_directed = True
    edge.allow_parallel_edges = False
    edge.from_id = "12345678-1234-5678-1234-567812345678"
    edge.to_id = "12345678-1234-5678-1234-567812345678"
    edge.type = "Test Type"
    edge.additional_attributes = {"example": "example"}
    edge.serialize.return_value = {
        "id": edge.id,
        "label": edge.label,
        "document": edge.document,
        "is_directed": edge.is_directed,
        "allow_parallel_edges": edge.allow_parallel_edges,
        "from_id": edge.from_id,
        "to_id": edge.to_id,
        "type": edge.type,
        **edge.additional_attributes,
    }
    return edge


def test_add_edge(chroma_db: ChromaDB, mock_edge: Mock) -> None:
    """Test that an edge is added to the collection with the correct data."""
    with patch.object(ChromaDB, "_validate_edge_type", return_value=True):
        chroma_db.add_edge(mock_edge)

        expected_data = mock_edge.serialize()
        chroma_db.collection.add.assert_called_with(
            ids=mock_edge.id, documents="Test Document", metadatas=expected_data
        )


def test_add_edge_error_handling(mock_edge: Mock, chroma_db: ChromaDB) -> None:
    """Test that errors are handled correctly when adding an edge."""
    mock_edge.id = "test_id"
    mock_edge.serialize.side_effect = Exception("Test Exception")

    with patch.object(ChromaDB, "_validate_edge_type", return_value=True):
        with pytest.raises(Exception) as excinfo1:
            chroma_db.add_edge(mock_edge)
        assert "Test Exception" in str(excinfo1.value)

    with pytest.raises(TypeError) as excinfo2:
        chroma_db.add_edge("test")  # type: ignore # wrong type

    assert "Expected edge to be of type Edge" in str(excinfo2.value)


def test_get_edge_success(chroma_db: ChromaDB, mock_edge: Mock) -> None:
    """Test that an edge is returned when it exists."""
    mock_response: dict[str, list[PrimitiveType]] = {
        "metadatas": [mock_edge.serialize()]
    }
    chroma_db.collection.get.return_value = mock_response

    result: Edge | None = chroma_db.get_edge(mock_edge.id)

    assert result is not None
    assert result.id == mock_edge.id
    chroma_db.collection.get.assert_called_with(mock_edge.id)


def test_get_edge_non_existent(chroma_db: ChromaDB) -> None:
    """Test that None is returned when an edge does not exist."""
    chroma_db.collection.get.return_value = None

    result: Edge | None = chroma_db.get_edge("non_existent_id")
    assert result is None
    chroma_db.collection.get.assert_called_with("non_existent_id")


@pytest.mark.parametrize(
    "arg, expected",
    [
        (True, False),
        (1, False),
        ([], False),
        ({"a": "b"}, False),
        (Node(), True),
        (Edge(to_id="1", from_id="2"), False),
    ],
)
def test_validate_node_type(arg: Node, expected: bool, chroma_db: ChromaDB) -> None:
    """Test that a TypeError is raised if the node is not of type Node."""
    result: bool = chroma_db._validate_node_type(arg)
    assert result == expected


@pytest.mark.parametrize(
    "arg, expected",
    [
        (True, False),
        (1, False),
        ([], False),
        ({"a": "b"}, False),
        (Node(), False),
        (Edge(to_id="1", from_id="2"), True),
    ],
)
def test_validate_edge_type(arg: Edge, expected: bool, chroma_db: ChromaDB) -> None:
    """Test that a TypeError is raised if the edge is not of type Edge."""
    result: bool = chroma_db._validate_edge_type(arg)
    assert result == expected
