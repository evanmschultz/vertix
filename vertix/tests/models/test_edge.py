from unittest.mock import patch
from pydantic import ValidationError
import pytest

from vertix.models import Edge
import vertix.tests.helpers.helper_functions as helper
from vertix.typings import PrimitiveType


@pytest.mark.parametrize(
    "from_id, to_id, type, is_directed, allow_parallel_edges, should_raise",
    [
        ("1", "2", "edge", True, False, False),
        ("1", "2", "edge", "invalid", False, True),
        ("1", "2", "edge", False, "invalid", True),
        ((), "2", "edge", True, True, True),
        ("1", None, "edge", True, True, True),
        ("1", "2", 123, True, True, True),
    ],
)
def test_edge_model(
    from_id: str,
    to_id: str,
    type: str,
    is_directed: bool,
    allow_parallel_edges: bool,
    should_raise: bool,
) -> None:
    """Test that Edge model is validated correctly."""
    if should_raise:
        with pytest.raises(ValidationError):
            Edge(
                is_directed=is_directed,
                allow_parallel_edges=allow_parallel_edges,
                from_id=from_id,
                to_id=to_id,
                edge_type=type,
            )
    else:
        helper.try_except_block_handler(
            lambda: Edge(
                is_directed=is_directed,
                allow_parallel_edges=allow_parallel_edges,
                from_id=from_id,
                to_id=to_id,
                edge_type=type,
            ),
            ValidationError,
            "Unexpected ValidationError for Edge model instantiation",
        )


@pytest.mark.parametrize(
    "from_id, to_id, edge_type, is_directed, allow_parallel_edges, should_raise",
    [
        ("1", "2", "edge", True, False, False),
        ("1", "2", "edge", "invalid", False, True),
        ("1", "2", "edge", False, "invalid", True),
        ((), "2", "edge", True, True, True),
        ("1", None, "edge", True, True, True),
        ("1", "2", 123, True, True, True),
    ],
)
def test_edge_attribute_assignment_validation(
    from_id: str,
    to_id: str,
    edge_type: str,
    is_directed: bool,
    allow_parallel_edges: bool,
    should_raise: bool,
) -> None:
    """Test that Edge attribute assignment is validated correctly."""
    edge = Edge(
        from_id="example_from_id",
        to_id="example_to_id",
    )
    if should_raise:
        with pytest.raises(ValidationError):
            edge.from_id = from_id
            edge.to_id = to_id
            edge.edge_type = edge_type
            edge.is_directed = is_directed
            edge.allow_parallel_edges = allow_parallel_edges
    else:
        helper.try_except_block_handler(
            lambda: helper.set_attributes(
                edge,
                {
                    "from_id": from_id,
                    "to_id": to_id,
                    "edge_type": edge_type,
                    "is_directed": is_directed,
                    "allow_parallel_edges": allow_parallel_edges,
                },
            ),
            ValidationError,
            "Unexpected ValidationError for Edge model assignment",
        )


def test_edge_model_serialization() -> None:
    """Test serialization of Edge model."""
    base_model = Edge(
        id="test_id",
        label="test_label",
        document="test_document",
        from_id="test_from_id",
        to_id="test_to_id",
        created_at="2021-01-01T00:00:00.000000",
        updated_at="2021-01-01T00:00:00.000000",
        additional_attributes={"test_attribute": True, "test_attribute2": 123},
    )
    expected_serialization: dict[str, PrimitiveType] = {
        "id": "test_id",
        "label": "test_label",
        "document": "test_document",
        "from_id": "test_from_id",
        "to_id": "test_to_id",
        "edge_type": "edge",
        "is_directed": True,
        "allow_parallel_edges": False,
        "created_at": "2021-01-01T00:00:00.000000",
        "test_attribute": True,
        "test_attribute2": 123,
    }

    serialized_model: dict[str, PrimitiveType] = base_model.serialize()
    updated_at = serialized_model.pop("updated_at")
    assert isinstance(updated_at, str)
    assert updated_at > base_model.created_at
    assert serialized_model == expected_serialization


def test_edge_model_serialization_exception_handling() -> None:
    """Test exception handling when serializing Edge model."""
    model = Edge(from_id="test_from_id", to_id="test_to_id")

    with patch.object(Edge, "model_dump", side_effect=Exception("Serialization Error")):
        with pytest.raises(Exception) as excinfo:
            model.serialize()
        assert "Serialization Error" in str(excinfo.value)


@pytest.mark.parametrize(
    "from_id, to_id, edge_type, is_directed, allow_parallel_edges, should_raise",
    [
        ("test_from_id", "test_to_id", "test_edge_type", True, False, False),
        (True, "test_to_id", "test_edge_type", True, False, True),
        ("test_from_id", 1, "test_edge_type", True, False, True),
        ("test_from_id", "test_to_id", None, True, False, True),
        ("test_from_id", "test_to_id", "test_edge_type", (), True, True),
        ("test_from_id", "test_to_id", "test_edge_type", True, [], True),
    ],
)
def test_edge_model_deserialization(
    from_id: str,
    to_id: str,
    edge_type: str,
    is_directed: bool,
    allow_parallel_edges: bool,
    should_raise: bool,
) -> None:
    """Test deserialization of Edge model"""
    serialized_dict: dict[str, PrimitiveType] = {
        "from_id": from_id,
        "to_id": to_id,
        "edge_type": edge_type,
        "is_directed": is_directed,
        "allow_parallel_edges": allow_parallel_edges,
    }
    if should_raise:
        with pytest.raises(TypeError):
            Edge.deserialize(serialized_dict)
    else:
        helper.try_except_block_handler(
            lambda: Edge.deserialize(serialized_dict),
            ValidationError,
            "Unexpected ValidationError for Edge model deserialization",
        )
        deserialized: Edge = Edge.deserialize(serialized_dict)
        assert isinstance(deserialized, Edge)
        assert deserialized.from_id == from_id
        assert deserialized.to_id == to_id
        assert deserialized.edge_type == edge_type
        assert deserialized.is_directed == is_directed
        assert deserialized.allow_parallel_edges == allow_parallel_edges
