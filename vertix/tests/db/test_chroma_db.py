import pytest
from unittest.mock import Mock, create_autospec, patch

from vertix.db import ChromaDB
import vertix.db.db_utilities as db_utils
from vertix import NodeModel, EdgeModel
from vertix.typings import PrimitiveType, chroma_types
from vertix.typings.db import QueryReturn, QueryInclude


@pytest.fixture
def chroma_db() -> ChromaDB:
    """Return a ChromaDB instance."""
    collection_mock = create_autospec(chroma_types.Collection)
    return ChromaDB(collection=collection_mock)


def test_chroma_db_initialization(chroma_db: ChromaDB) -> None:
    """Test that the ChromaDB instance is initialized correctly."""
    assert chroma_db.collection is not None


@pytest.fixture()
def mock_node() -> Mock:
    """Return a mock Node object."""
    node = create_autospec(NodeModel)
    node.id = "12345678-1234-5678-1234-567812345678"
    node.vrtx_model_type = "node"
    node.label = "Test Node"
    node.document = "Test Document"
    node.additional_attributes = {"example": "example"}
    node.serialize.return_value = {
        "id": node.id,
        "vrtx_model_type": node.vrtx_model_type,
        "label": node.label,
        "document": node.document,
        **node.additional_attributes,
    }
    return node


@pytest.fixture
def mock_edge() -> Mock:
    """Return a mock Edge object."""
    edge = Mock()
    edge.id = "12345678-1234-5678-1234-567812345678"
    edge.vrtx_model_type = "edge"
    edge.document = "Test Document"
    edge.from_id = "12345678-1234-5678-1234-567812345678"
    edge.to_id = "12345678-1234-5678-1234-567812345678"
    edge.additional_attributes = {"example": "example"}
    edge.serialize.return_value = {
        "id": edge.id,
        "vrtx_model_type": edge.vrtx_model_type,
        "document": edge.document,
        "from_id": edge.from_id,
        "to_id": edge.to_id,
        **edge.additional_attributes,
    }
    return edge


def test_add(chroma_db: ChromaDB, mock_node: Mock, mock_edge: Mock) -> None:
    """Test that a NodeModel or EdgeModel is added to the collection with the correct data."""
    with patch.object(db_utils, "validate_model_type", return_value=True):
        chroma_db.add(mock_node)

        expected_data = mock_node.serialize()
        chroma_db.collection.add.assert_called_with(
            ids=mock_node.id, documents="Test Document", metadatas=expected_data
        )

    with patch.object(db_utils, "validate_model_type", return_value=True):
        chroma_db.add(mock_edge)

        expected_data = mock_edge.serialize()
        chroma_db.collection.add.assert_called_with(
            ids=mock_edge.id, documents="Test Document", metadatas=expected_data
        )


def test_add_error_handling(
    mock_node: Mock, mock_edge: Mock, chroma_db: ChromaDB
) -> None:
    """Test that errors are handled correctly when adding to collection."""
    mock_node.serialize.side_effect = Exception("Test Exception")
    with patch.object(db_utils, "validate_model_type", return_value=True):
        with pytest.raises(Exception) as excinfo1:
            chroma_db.add(mock_node)
        assert "Test Exception" in str(excinfo1.value)

    with pytest.raises(TypeError) as excinfo2:
        chroma_db.add("test")  # type: ignore # wrong type
    assert "Expected model to be of type `NodeModel` or `EdgeModel`" in str(
        excinfo2.value
    )


def test_get_by_id_success(
    chroma_db: ChromaDB, mock_node: Mock, mock_edge: Mock
) -> None:
    """Test that a node is returned when it exists."""
    # Tests for NodeModel
    node_mock_response: dict[str, list[PrimitiveType]] = {
        "metadatas": [mock_node.serialize()]
    }
    chroma_db.collection.get.return_value = node_mock_response
    node_result = chroma_db.get_by_id(mock_node.id)
    assert node_result is not None
    assert node_result.id == mock_node.id
    chroma_db.collection.get.assert_called_with(mock_node.id)

    # Tests for EdgeModel
    edge_mock_response: dict[str, list[PrimitiveType]] = {
        "metadatas": [mock_edge.serialize()]
    }
    chroma_db.collection.get.return_value = edge_mock_response
    edge_result = chroma_db.get_by_id(mock_edge.id)
    assert edge_result is not None
    assert edge_result.id == mock_edge.id
    chroma_db.collection.get.assert_called_with(mock_edge.id)


def test_get_by_id_non_existent(chroma_db: ChromaDB) -> None:
    """Test that None is returned when a node does not exist."""
    chroma_db.collection.get.return_value = None

    result = chroma_db.get_by_id("non_existent_id")
    assert result is None
    chroma_db.collection.get.assert_called_with("non_existent_id")


def test_get_by_id_missing_metadata(chroma_db: ChromaDB) -> None:
    """Test that None is returned when metadata is missing from the edge data."""
    chroma_db.collection.get.return_value = {"metadatas": []}

    result = chroma_db.get_by_id("edge_id_with_missing_metadata")
    assert result is None
    chroma_db.collection.get.assert_called_with("edge_id_with_missing_metadata")


def test_get_by_id_invalid_metadata(chroma_db: ChromaDB) -> None:
    """Test that TypeError is raised when metadata is not a dict."""
    invalid_metadata: list[str] = ["not a dict"]
    chroma_db.collection.get.return_value = {"metadatas": invalid_metadata}

    with pytest.raises(TypeError):
        chroma_db.get_by_id("some_id")


def test_get_by_id_metadata_missing_vrtx_model_type_or_invalid_value(
    chroma_db: ChromaDB, mock_node: Mock, mock_edge: Mock
) -> None:
    """Test that TypeError is raised when metadata is missing the vrtx_model_type key."""
    metadata_dict: dict[str, PrimitiveType] = mock_node.serialize()
    metadata_dict.pop("vrtx_model_type")
    node_mock_response: dict[str, list[dict[str, PrimitiveType]]] = {
        "metadatas": [metadata_dict]
    }

    chroma_db.collection.get.return_value = node_mock_response
    with pytest.raises(KeyError):
        chroma_db.get_by_id(mock_node.id)

    metadata_dict["vrtx_model_type"] = "invalid_type"
    node_mock_response = {"metadatas": [metadata_dict]}
    chroma_db.collection.get.return_value = node_mock_response
    with pytest.raises(ValueError):
        chroma_db.get_by_id(mock_node.id)


def test_get_all(chroma_db: ChromaDB) -> None:
    """Test that all nodes are returned when they exist."""
    mock_response: dict[str, list[dict[str, str]]] = {
        "metadatas": [
            {
                "id": "test_node_id",
                "vrtx_model_type": "node",
                "label": "test_label",
                "created_at": "2021-01-01T00:00:00.000000",
                "updated_at": "2021-01-01T00:00:00.000000",
            },
            {
                "id": "test_edge_id",
                "vrtx_model_type": "edge",
                "from_id": "1",
                "to_id": "2",
                "created_at": "2021-01-01T00:00:00.000000",
                "updated_at": "2021-01-01T00:00:00.000000",
            },
        ]
    }
    chroma_db.collection.get.return_value = mock_response
    result: list[NodeModel | EdgeModel] | None = chroma_db.get_all()
    assert result is not None
    assert result[0].id == "test_node_id"
    assert result[1].id == "test_edge_id"
    chroma_db.collection.get.assert_called_with()


def test_get_all_empty(chroma_db: ChromaDB) -> None:
    """Test that None is returned when no nodes exist."""
    chroma_db.collection.get.return_value = None
    result: list[NodeModel | EdgeModel] | None = chroma_db.get_all()
    assert result is None
    chroma_db.collection.get.assert_called_with()


def test_get_all_missing_metadata(chroma_db: ChromaDB) -> None:
    """Test that None is returned when metadata is missing from the edge data."""
    chroma_db.collection.get.return_value = {"metadatas": []}
    result = chroma_db.get_all()
    assert result is None
    chroma_db.collection.get.assert_called_with()


def test_update_by_id(chroma_db: ChromaDB) -> None:
    """Test successful update of an existing node."""
    existing_node = NodeModel(
        id="test_node_id",
        label="test_label",
        created_at="2021-01-01T00:00:00.000000",
        updated_at="2021-01-01T00:00:00.000000",
    )

    updated_node = NodeModel(id="test_node_id", label=existing_node.label)
    with patch.object(ChromaDB, "get_by_id", return_value=existing_node):
        chroma_db.update(updated_node)

    assert updated_node.created_at == existing_node.created_at

    existing_edge = EdgeModel(
        id="test_edge_id",
        from_id="1",
        to_id="2",
        created_at="2021-01-01T00:00:00.000000",
        updated_at="2021-01-01T00:00:00.000000",
    )

    updated_edge = EdgeModel(
        id="test_edge_id",
        from_id="11",
        to_id="22",
    )
    with patch.object(ChromaDB, "get_by_id", return_value=existing_edge):
        chroma_db.update(updated_edge)

    assert updated_edge.created_at == existing_edge.created_at


def test_update_by_id_non_existent(chroma_db: ChromaDB) -> None:
    """Test that the update_node method does nothing if the node does not exist."""
    non_existent_node = NodeModel(id="non_existent_id", label="test_label")

    with patch.object(db_utils, "validate_model_type", return_value=True):
        with patch.object(ChromaDB, "get_by_id", return_value=None):
            chroma_db.update(non_existent_node)

        # chroma_db.update(non_existent_node)

        chroma_db.collection.update.assert_not_called()


def test_update_by_id_validate_model_type_error(chroma_db: ChromaDB) -> None:
    """Test that TypeError is raised if the input is not a NodeModel or EdgeModel."""
    not_a_valid_model = "this is not a node"
    with pytest.raises(TypeError) as exc_info:
        chroma_db.update(not_a_valid_model)  # type: ignore
    assert "Expected model to be of type" in str(exc_info.value)


def test_update_try_except(chroma_db: ChromaDB) -> None:
    """Test that exceptions are handled correctly when using ChromaDB's `update` method."""
    with patch(
        "vertix.models.NodeModel.serialize", side_effect=Exception("Update failed")
    ):
        node = NodeModel(
            created_at="2021-01-01T00:00:00.000000",
            updated_at="2021-01-01T00:00:00.000000",
            label="Test Node",
        )
        with patch("vertix.db.ChromaDB.get_by_id", return_value=node):
            with pytest.raises(Exception) as exc_info:
                chroma_db.update(node)

        assert f"Could not update model with id `{node.id}`: Update failed" in str(
            exc_info.value
        )


@pytest.mark.parametrize(
    "arg, expected",
    [
        (NodeModel(label="Test Node"), True),
        (EdgeModel(to_id="1", from_id="2"), True),
        (True, False),
        (1, False),
        ([], False),
        ({"a": "b"}, False),
    ],
)
def test_validate_model_type(
    arg: EdgeModel, expected: bool, chroma_db: ChromaDB
) -> None:
    """Test that a TypeError is raised if the edge is not of type Edge."""
    result: bool = db_utils.validate_model_type(arg)
    assert result == expected


def test_delete_exception_handling(chroma_db: ChromaDB) -> None:
    """Test that exceptions are handled correctly when deleting by id."""
    chroma_db.collection.delete.side_effect = Exception("Test Exception")

    with pytest.raises(Exception) as excinfo:
        chroma_db.delete_by_id("test_id")
    assert "Test Exception" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo2:
        chroma_db.delete_by_where_filter({"id": "test_id"})
    assert "Test Exception" in str(excinfo2.value)


def test_query_success(chroma_db: ChromaDB) -> None:
    """Test that the query method returns the expected result."""
    query_result_example = chroma_types.QueryResult(
        ids=["id1", "id2"],  # type: ignore
        embeddings=[[0.1, 0.2, 0.3], None],  # type: ignore
        documents=[["Document 1 content"], None],  # type: ignore
        uris=[["http://example.com/1"], None],  # type: ignore
        data=[["data1"], None],  # type: ignore
        metadatas=[
            [{"id": "test_node", "label": "test label", "vrtx_model_type": "node"}],
            [
                {
                    "id": "test_edge",
                    "vrtx_model_type": "edge",
                    "from_id": "from_id",
                    "to_id": "to_id",
                }
            ],
        ],  # type: ignore
        distances=[[1.0, 2.0], [3.0, 4.0]],
    )
    chroma_db.collection.query.return_value = query_result_example
    result: list[QueryReturn] | None = chroma_db.query(
        queries=["test_query"], table="nodes", include=[QueryInclude.DOCUMENTS]
    )
    assert result
    assert len(result) == 2
    assert result[0].model.id == "test_node"
    assert result[1].model.id == "test_edge"

    chroma_db.collection.query.side_effect = Exception("Test Exception")
    with pytest.raises(Exception) as excinfo:
        chroma_db.query(
            queries=["test_query"], table="nodes", include=[QueryInclude.DOCUMENTS]
        )
    assert "Test Exception" in str(excinfo.value)
