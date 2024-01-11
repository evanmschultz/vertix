from unittest.mock import patch
from pydantic import ValidationError
import pytest

from vertix.models import Node
from vertix.typings import PrimitiveType


@pytest.mark.parametrize(
    "description, node_type, neighbors_count, should_raise",
    [
        ("Test Description", "node", 5, False),
        ((), "node", 0, True),
        ("Test Description", "node", "abc", True),
        ("Test Description", "node", -1, True),
        ("Test Description", 123, 5, True),
    ],
)
def test_node_model(
    node_type: str,
    description: str,
    neighbors_count: int,
    should_raise: bool,
) -> None:
    """Test that Node model is validated correctly."""
    if should_raise:
        with pytest.raises(ValidationError):
            Node(
                node_type=node_type,
                description=description,
                neighbors_count=neighbors_count,
            )
    else:
        try:
            Node(
                node_type=node_type,
                description=description,
                neighbors_count=neighbors_count,
            )
        except ValidationError:
            pytest.fail("Unexpected ValidationError for valid values")


@pytest.mark.parametrize(
    "description, node_type, neighbors_count, should_raise",
    [
        ("Test Description", "test_node_type", 4, False),
        ((), "test_node_type", 0, True),
        ("Test Description", None, 0, True),
        ("Test Description", "test_node_type", -1, True),
        ("Test Description", "test_node_type", 1.2, True),
    ],
)
def test_node_attribute_assignment_validation(
    description: str,
    node_type: str,
    neighbors_count: int,
    should_raise: bool,
) -> None:
    """Test that attributes are validated correctly"""
    node = Node()
    if should_raise:
        with pytest.raises(ValidationError):
            node.description = description
            node.node_type = node_type
            node.neighbors_count = neighbors_count
    else:
        try:
            node.description = description
            node.node_type = node_type
            node.neighbors_count = neighbors_count
        except ValidationError:
            pytest.fail("Unexpected ValidationError for valid values")


def test_node_model_serialization() -> None:
    """Test serialization of Node model."""
    base_model = Node(
        id="test_id",
        created_at="2021-01-01T00:00:00.000000",
        updated_at="2021-01-01T00:00:00.000000",
        description="Test Description",
        node_type="test_node_type",
        neighbors_count=5,
        additional_attributes={"test_attribute": True, "test_attribute2": 123},
    )
    expected_serialization: dict[str, PrimitiveType] = {
        "id": "test_id",
        "label": "",
        "document": "",
        "created_at": "2021-01-01T00:00:00.000000",
        "description": "Test Description",
        "node_type": "test_node_type",
        "neighbors_count": 5,
        "test_attribute": True,
        "test_attribute2": 123,
    }

    serialized_model: dict[str, PrimitiveType] = base_model.serialize()
    updated_at = serialized_model.pop("updated_at")
    assert isinstance(updated_at, str)
    assert updated_at > base_model.created_at
    assert serialized_model == expected_serialization


def test_node_model_serialization_exception_handling() -> None:
    """Test serialization exception handling of Node model."""
    model = Node()

    with patch.object(Node, "model_dump", side_effect=Exception("Serialization Error")):
        with pytest.raises(Exception) as excinfo:
            model.serialize()
        assert "Serialization Error" in str(excinfo.value)


@pytest.mark.parametrize(
    "description, node_type, neighbors_count, should_raise",
    [
        ("test description", "test_node_type", 0, False),
        (None, "test_node_type", 0, True),
        ("test description", (), 0, True),
        ("test description", "test_node_type", 1.2, True),
    ],
)
def test_node_model_deserialization(
    description: str,
    node_type: str,
    neighbors_count: int,
    should_raise: bool,
) -> None:
    """Test deserialization of Node model."""
    serialized_dict: dict[str, PrimitiveType] = {
        "description": description,
        "node_type": node_type,
        "neighbors_count": neighbors_count,
    }
    if should_raise:
        with pytest.raises(TypeError):
            Node.deserialize(serialized_dict)
    else:
        try:
            deserialized: Node = Node.deserialize(serialized_dict)
            assert deserialized.description == description
            assert deserialized.node_type == node_type
            assert deserialized.neighbors_count == neighbors_count

        except ValidationError:
            pytest.fail("Unexpected ValidationError for valid values")
