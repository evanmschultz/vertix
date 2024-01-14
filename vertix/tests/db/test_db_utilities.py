import pytest

import vertix.db.db_utilities as db_utils
from vertix import NodeModel, EdgeModel
from vertix.typings import PrimitiveType


def test_validate_model_type() -> None:
    """Test that the validate_model_type function returns True if the model is of type Node or Edge."""
    assert db_utils.validate_model_type(NodeModel()) is True
    assert db_utils.validate_model_type(EdgeModel(from_id="1", to_id="2")) is True
    assert db_utils.validate_model_type("test") is False  # type: ignore


def test_return_model() -> None:
    """Test that the return_model function returns a NodeModel or EdgeModel based on the metadata."""
    node_data: dict[str, PrimitiveType] = NodeModel(id="node").serialize()
    edge_data: dict[str, PrimitiveType] = EdgeModel(
        id="edge", from_id="1", to_id="2"
    ).serialize()

    node: NodeModel | EdgeModel = db_utils.return_model(node_data)
    edge: NodeModel | EdgeModel = db_utils.return_model(edge_data)

    assert isinstance(node, NodeModel) is True
    assert isinstance(edge, EdgeModel) is True
    assert node.id == "node"
    assert edge.id == "edge"


def test_confirm_metadatas_success() -> None:
    """Test that the confirm_metadatas function returns the metadatas if they are valid."""
    metadatas: list[dict[str, PrimitiveType]] = [
        NodeModel(id="node").serialize(),
        EdgeModel(id="edge", from_id="1", to_id="2").serialize(),
    ]

    assert db_utils.confirm_metadatas(metadatas) == metadatas


def test_confirm_metadatas_errors() -> None:
    """Test that the error handling in the `confirm_metadatas` function are working as expected."""
    metadatas: list[str] = ["not_a_dict"]
    with pytest.raises(TypeError) as exc_info:
        db_utils.confirm_metadatas(metadatas)  # type: ignore
    assert (
        str(exc_info.value)
        == "Metadatas from ChromaDB collection are not of type `dict`"
    )
    with pytest.raises(KeyError) as exc_info_2:
        db_utils.confirm_metadatas([{"not_id": "123"}])
    assert "`vrtx_model_type` not" in str(exc_info_2.value)
