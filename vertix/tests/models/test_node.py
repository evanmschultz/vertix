from unittest.mock import patch
from hypothesis import given, strategies
from pydantic import ValidationError
import pytest

from vertix.models import NodeModel
import vertix.tests.helpers.helper_functions as helper
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
            NodeModel(
                node_type=node_type,
                description=description,
                neighbors_count=neighbors_count,
            )
    else:
        helper.try_except_block_handler(
            lambda: NodeModel(
                node_type=node_type,
                description=description,
                neighbors_count=neighbors_count,
            ),
            ValidationError,
            "Unexpected ValidationError for Node model instantiation",
        )


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
    node = NodeModel()
    if should_raise:
        with pytest.raises(ValidationError):
            node.description = description
            node.node_type = node_type
            node.neighbors_count = neighbors_count
    else:
        helper.try_except_block_handler(
            lambda: helper.set_attributes(
                node,
                {
                    "description": description,
                    "node_type": node_type,
                    "neighbors_count": neighbors_count,
                },
            ),
            ValidationError,
            "Unexpected ValidationError for Node attribute assignment",
        )


def test_node_model_serialization() -> None:
    """Test serialization of Node model."""
    base_model = NodeModel(
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
        "vrtx_model_type": "node",
        "table": "nodes",
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
    model = NodeModel()

    with patch.object(
        NodeModel, "model_dump", side_effect=Exception("Serialization Error")
    ):
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
        with pytest.raises(ValidationError):
            NodeModel.deserialize(serialized_dict)
    else:
        helper.try_except_block_handler(
            lambda: NodeModel.deserialize(serialized_dict),
            ValidationError,
            "Unexpected ValidationError for Node model deserialization",
        )
        deserialized: NodeModel = NodeModel.deserialize(serialized_dict)
        assert isinstance(deserialized, NodeModel)
        assert deserialized.description == description
        assert deserialized.node_type == node_type
        assert deserialized.neighbors_count == neighbors_count


@given(
    vrtx_model_type=strategies.text().filter(lambda x: x != "node"),
)
def test_vrtx_model_type(vrtx_model_type: str) -> None:
    """Test that vrtx_model_type is frozen."""
    node = NodeModel()
    with pytest.raises(ValidationError):
        node.vrtx_model_type = vrtx_model_type  # type: ignore

    with pytest.raises(ValidationError):
        NodeModel(vrtx_model_type=vrtx_model_type)  # type: ignore
