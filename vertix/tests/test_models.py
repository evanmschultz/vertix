from datetime import datetime, timedelta
from unittest.mock import patch

from pydantic import ValidationError
import pytest

from vertix.models.base_graph_entity_model import BaseGraphEntityModel
from vertix.models import Node, Edge

from vertix.typings import PrimitiveType


def test_base_graph_entity_model_timestamp_validations() -> None:
    # Test validation errors for invalid format
    with pytest.raises(ValidationError):
        BaseGraphEntityModel(created_at=1)  # type: ignore # invalid type

    with pytest.raises(ValidationError):
        BaseGraphEntityModel(updated_at="invalid")  # invalid type

    # Test with valid timestamp strings
    valid_timestamp: str = datetime.utcnow().isoformat()
    try:
        BaseGraphEntityModel(created_at=valid_timestamp, updated_at=valid_timestamp)
    except ValidationError:
        pytest.fail("Unexpected ValidationError for valid timestamps")

    # Test created_at is later than updated_at
    later_timestamp: str = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    with pytest.raises(ValidationError):
        BaseGraphEntityModel(created_at=later_timestamp, updated_at=valid_timestamp)

    # Test updated_at and created_at are after current time
    with pytest.raises(ValidationError):
        BaseGraphEntityModel(created_at=later_timestamp, updated_at=later_timestamp)

    # Test created_at and updated_at are provided together
    with pytest.raises(ValidationError):
        BaseGraphEntityModel(created_at=valid_timestamp)  # missing updated_at

    with pytest.raises(ValidationError):
        BaseGraphEntityModel(updated_at=valid_timestamp)  # missing created_at


def test_node_model() -> None:
    # Test creating node with defaults
    node = Node()
    assert node.id
    assert node.label == ""
    assert node.description == ""
    assert node.type == "node"
    assert node.additional_attributes == {}
    assert node.neighbors_count == 0

    # Test setting additional attributes
    node.additional_attributes = {"test": "value"}
    assert node.additional_attributes == {"test": "value"}

    # Test serialize
    serialized: dict[str, PrimitiveType] = node.serialize()
    assert serialized["id"] == node.id
    assert serialized["test"] == "value"

    # Test created_at and updated_at timestamps are set in serialization
    assert len(node.created_at) > 1 and isinstance(node.created_at, str)
    assert len(node.updated_at) > 1 and isinstance(node.updated_at, str)
    assert serialized["created_at"] == serialized["updated_at"]


def test_node_validation() -> None:
    # Test validation errors
    with pytest.raises(TypeError):
        Node(additional_attributes="invalid")  # type: ignore # invalid type

    with pytest.raises(TypeError):
        node = Node()
        node.additional_attributes = {"key": []}  # type: ignore # invalid type


def test_node_timestamps_from_created_model() -> None:
    # Test created_at and updated_at timestamps are set in serialization
    node = Node(
        created_at="2021-01-01T00:00:00.000000", updated_at="2021-01-01T00:00:00.000000"
    )
    assert node.created_at == "2021-01-01T00:00:00.000000"
    assert node.created_at == node.updated_at

    node.serialize()
    assert node.created_at == "2021-01-01T00:00:00.000000"
    assert node.created_at != node.updated_at


def test_edge_model() -> None:
    # Create connected nodes
    node1 = Node(id="1")
    node2 = Node(id="2")

    # Test edge creation
    edge = Edge(from_id=node1.id, to_id=node2.id)
    assert edge.from_id == "1"
    assert edge.to_id == "2"
    assert edge.type == "edge"
    assert edge.is_directed is True
    assert edge.allow_parallel_edges is False
    assert edge.label == ""

    # Test updating attributes
    edge.is_directed = False
    assert edge.is_directed is False

    # Test serialization
    serialized: dict[str, PrimitiveType] = edge.serialize()
    assert serialized["from_id"] == "1"
    assert serialized["to_id"] == "2"
    assert serialized["type"] == "edge"
    assert serialized["is_directed"] is False
    assert serialized["allow_parallel_edges"] is False
    assert serialized["label"] == ""

    # Test created_at and updated_at timestamps are set in serialization
    assert len(edge.created_at) > 1 and isinstance(edge.created_at, str)
    assert len(edge.updated_at) > 1 and isinstance(edge.updated_at, str)
    assert serialized["created_at"] == serialized["updated_at"]


def test_edge_model_serialization_with_no_custom_values() -> None:
    # Create connected nodes
    node1 = Node(id="1")
    node2 = Node(id="2")

    # Test edge creation with no custom values
    edge = Edge(from_id=node1.id, to_id=node2.id)
    assert edge.from_id == "1"
    assert edge.to_id == "2"
    assert edge.type == "edge"
    assert edge.is_directed is True
    assert edge.allow_parallel_edges is False
    assert edge.label == ""

    # Test updating attributes
    edge.is_directed = False
    assert edge.is_directed is False

    # Test serialization
    serialized: dict[str, PrimitiveType] = edge.serialize()
    assert serialized["from_id"] == "1"
    assert serialized["to_id"] == "2"
    assert serialized["type"] == "edge"
    assert serialized["is_directed"] is False
    assert serialized["allow_parallel_edges"] is False
    assert serialized["label"] == ""
    with pytest.raises(KeyError):
        serialized["additional_attributes"]


def test_edge_model_with_custom_values() -> None:
    # Create connected nodes
    node1 = Node(id="1")
    node2 = Node(id="2")

    # Test edge creation with custom values
    edge = Edge(
        from_id=node1.id,
        to_id=node2.id,
        type="custom_edge",
        is_directed=False,
        allow_parallel_edges=True,
        label="Custom Edge",
        additional_attributes={"key": "value"},
    )
    assert edge.from_id == "1"
    assert edge.to_id == "2"
    assert edge.type == "custom_edge"
    assert edge.is_directed is False
    assert edge.allow_parallel_edges is True
    assert edge.label == "Custom Edge"
    assert edge.additional_attributes == {"key": "value"}

    # Test updating attributes
    edge.is_directed = True
    assert edge.is_directed is True

    # Test serialization
    serialized: dict[str, PrimitiveType] = edge.serialize()
    assert serialized["from_id"] == "1"
    assert serialized["to_id"] == "2"
    assert serialized["type"] == "custom_edge"
    assert serialized["is_directed"] is True
    assert serialized["allow_parallel_edges"] is True
    assert serialized["label"] == "Custom Edge"
    assert serialized["key"] == "value"


def test_edge_model_validation() -> None:
    # Test validation errors
    with pytest.raises(ValidationError):
        Edge(from_id="1")  # type: ignore # missing to_id

    with pytest.raises(ValidationError):
        Edge(to_id="2")  # type: ignore # missing from_id

    with pytest.raises(TypeError):
        Edge(
            from_id="1", to_id="2", additional_attributes="invalid"  # type: ignore # invalid type
        )  # invalid additional_attributes type


def test_edge_model_attribute_update_validation() -> None:
    # Test attribute update validation errors
    edge = Edge(from_id="1", to_id="2")

    with pytest.raises(ValidationError):
        edge.is_directed = "invalid"  # type: ignore # invalid is_directed type

    with pytest.raises(ValidationError):
        edge.allow_parallel_edges = "invalid"  # type: ignore # invalid allow_parallel_edges type


def test_edge_timestamps_from_created_model() -> None:
    # Test updated_at timestamp is updated on serialization with existing data
    edge = Edge(
        to_id="1",
        from_id="2",
        created_at="2021-01-01T00:00:00.000000",
        updated_at="2021-01-01T00:00:00.000000",
    )
    assert edge.created_at == "2021-01-01T00:00:00.000000"
    assert edge.created_at == edge.updated_at

    edge.serialize()
    assert edge.created_at == "2021-01-01T00:00:00.000000"
    assert edge.created_at != edge.updated_at


def test_base_graph_entity_model_additional_attributes_validation() -> None:
    with pytest.raises(TypeError):
        BaseGraphEntityModel(additional_attributes="not a dict")  # type: ignore # should be a dict

    with pytest.raises(TypeError):
        BaseGraphEntityModel(additional_attributes={123: "value"})  # type: ignore # key not a string

    with pytest.raises(TypeError):
        BaseGraphEntityModel(additional_attributes={"key": [1, 2, 3]})  # type: ignore # value not a primitive type


def test_base_graph_entity_model_timestamp_edge_cases() -> None:
    with pytest.raises(ValueError):
        BaseGraphEntityModel(created_at="not a timestamp")  # invalid format

    with pytest.raises(ValueError):
        BaseGraphEntityModel(updated_at="2025-01-01T00:00:00")  # future timestamp

    with pytest.raises(ValueError):
        BaseGraphEntityModel(
            created_at="2020-01-01T00:00:00", updated_at="2019-01-01T00:00:00"
        )  # created_at after updated_at


def test_base_graph_entity_model_serialization() -> None:
    model = BaseGraphEntityModel()
    assert model.created_at == ""
    assert model.updated_at == ""
    model = BaseGraphEntityModel(additional_attributes={"key": "value"})
    serialized: dict[str, PrimitiveType] = model.serialize()
    model_created_at: datetime = datetime.fromisoformat(model.created_at)
    model_updated_at: datetime = datetime.fromisoformat(model.updated_at)
    try:
        serialized_created_at: datetime = datetime.fromisoformat(serialized["created_at"])  # type: ignore # mypy doesn't like this
        serialized_updated_at: datetime = datetime.fromisoformat(serialized["updated_at"])  # type: ignore # mypy doesn't like this
    except KeyError:
        pytest.fail("Serialized model missing `created_at` or `updated_at` key")

    assert serialized_created_at == model_created_at
    assert serialized_updated_at == model_updated_at
    assert serialized["created_at"] == model.created_at
    assert serialized["updated_at"] == model.updated_at


def test_base_graph_entity_model_serialization_exception_handling() -> None:
    model = BaseGraphEntityModel()

    with patch.object(
        BaseGraphEntityModel, "model_dump", side_effect=Exception("Serialization Error")
    ):
        with pytest.raises(Exception) as excinfo:
            model.serialize()
        assert "Serialization Error" in str(excinfo.value)


def test_deserialize_node_success() -> None:
    data = {
        "id": "123",
        "label": "Test Node",
        "description": "A test node",
        "type": "node",
        "neighbors_count": 5,
    }
    node: Node = Node.deserialize(data)
    assert isinstance(node, Node)
    assert node.id == "123"
    assert node.label == "Test Node"
    assert node.description == "A test node"
    assert node.type == "node"
    assert node.neighbors_count == 5


def test_deserialize_with_type_mismatch() -> None:
    data = {
        "id": "123",
        "label": "Test Node",
        "neighbors_count": "Not a number",  # This should be an int
    }
    with pytest.raises(TypeError):
        Node.deserialize(data)  # type: ignore


def test_deserialize_with_missing_fields() -> None:
    data = {
        "id": "123",
        "label": "Test Node",
        # Missing other required fields
    }
    node = Node.deserialize(data)  # type: ignore
    assert node.description == ""
    # Assert other default values


def test_deserialize_with_additional_attributes() -> None:
    data = {"id": "123", "label": "Test Node", "new_field": "New Value"}
    node = Node.deserialize(data)  # type: ignore
    assert "new_field" in node.additional_attributes
    assert node.additional_attributes["new_field"] == "New Value"


def test_deserialize_edge_success() -> None:
    data = {
        "id": "e123",
        "label": "Test Edge",
        "from_id": "n1",
        "to_id": "n2",
        "is_directed": True,
        "allow_parallel_edges": False,
        "type": "custom_edge",
    }
    edge = Edge.deserialize(data)
    assert isinstance(edge, Edge)
    assert edge.id == "e123"
    assert edge.label == "Test Edge"
    assert edge.from_id == "n1"
    assert edge.to_id == "n2"
    assert edge.is_directed is True
    assert edge.allow_parallel_edges is False
    assert edge.type == "custom_edge"


def test_deserialize_edge_with_type_mismatch() -> None:
    data = {
        "id": "e123",
        "from_id": "n1",
        "to_id": "n2",
        "is_directed": "not a boolean",  # This should be a boolean
        "allow_parallel_edges": False,
    }
    with pytest.raises(TypeError):
        Edge.deserialize(data)


def test_deserialize_edge_with_missing_fields() -> None:
    data = {
        "id": "e123",
        "from_id": "n1",
        # Missing 'to_id' field
    }
    with pytest.raises(ValidationError):
        Edge.deserialize(data)  # type: ignore


def test_deserialize_edge_with_additional_attributes() -> None:
    data = {
        "id": "e123",
        "from_id": "n1",
        "to_id": "n2",
        "new_field": "New Value",  # Additional attribute not defined in Edge model
    }
    edge = Edge.deserialize(data)  # type: ignore
    assert "new_field" in edge.additional_attributes
    assert edge.additional_attributes["new_field"] == "New Value"
