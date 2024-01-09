from datetime import datetime, timedelta
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
