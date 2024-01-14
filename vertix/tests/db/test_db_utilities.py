import pytest

import vertix.db.db_utilities as db_utils
from vertix import NodeModel, EdgeModel
from vertix.typings import PrimitiveType, chroma_types
from vertix.typings.db import QueryInclude, QueryReturn


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


def test_process_query_return_success() -> None:
    """Test that the db_utils `process_query_return` function is working as expected."""
    query_result_example = chroma_types.QueryResult(
        ids=["id1", "id2"],  # type: ignore
        embeddings=[[0.1, 0.2, 0.3], None],  # type: ignore
        documents=[["Document 1 content"], None],  # type: ignore
        uris=[["http://example.com/1"], None],  # type: ignore
        data=[["data1"], None],  # type: ignore
        metadatas=[
            [{"id": "test_node", "vrtx_model_type": "node"}],
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
    query_returns: list[QueryReturn] = db_utils.process_query_return(
        query_result_example
    )
    assert len(query_returns) == 2
    assert query_returns[0].model.id == "test_node"
    assert query_returns[1].model.id == "test_edge"
    assert isinstance(query_returns[0].model, NodeModel)
    assert isinstance(query_returns[1].model, EdgeModel)


def test_update_where_filter() -> None:
    """Test that the db_utils `update_where_filter` function is working as expected."""
    where_filter = {"id": "test"}
    table = "test_table"
    where_filter_updated = db_utils.update_where_filter(
        None, where_filter  # type: ignore # FIXME: fix type error
    )
    assert where_filter_updated == {"id": "test"}
    where_filter_updated_2 = db_utils.update_where_filter(
        table, where_filter  # type: ignore # FIXME: fix type error
    )
    assert where_filter_updated_2 == {"id": "test", "table": "test_table"}


def test_ensure_metadatas_in_include() -> None:
    """Test that the db_utils `ensure_metadatas_in_include` function is working as expected."""
    include_list = [QueryInclude.DOCUMENTS]
    include_list_updated = db_utils.ensure_metadatas_in_include(include_list)
    assert include_list_updated == [
        QueryInclude.DOCUMENTS,
        QueryInclude.METADATAS,
    ]
    include_list_updated_2 = db_utils.ensure_metadatas_in_include(
        [QueryInclude.EMBEDDINGS]
    )
    assert include_list_updated_2 == [QueryInclude.EMBEDDINGS, QueryInclude.METADATAS]


def test_process_query_return_failure() -> None:
    query_result_fail_1 = None
    with pytest.raises(Exception) as exc_info:
        db_utils.process_query_return(query_result_fail_1)  # type: ignore
    query_result_fail_2 = {"metadatas": None}
    with pytest.raises(Exception) as exc_info_2:
        db_utils.process_query_return(query_result_fail_2)  # type: ignore
    assert str(exc_info.value) == "ChromaDB query failed to return anything"
    assert str(exc_info_2.value) == "ChromaDB query failed to return anything"
