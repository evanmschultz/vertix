from pydantic import ValidationError
import pytest
from vertix.models.models import Node, Edge, PrimitiveType


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


def test_node_validation() -> None:
    # Test validation errors
    with pytest.raises(TypeError):
        Node(additional_attributes="invalid")  # type: ignore # invalid type

    with pytest.raises(TypeError):
        node = Node()
        node.additional_attributes = {"key": []}  # type: ignore # invalid type


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
