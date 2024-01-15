import logging
from vertix.models import NodeModel, EdgeModel
from vertix.typings import PrimitiveType, chroma_types
from vertix.typings.db import QueryInclude, QueryReturn


def validate_model_type(model: NodeModel | EdgeModel) -> bool:
    """
    Validates that the model is of type Node or Edge and returns a boolean.

    Args:
        - `model` (Node | Edge): The model to validate.

    Returns:
        - `bool`: True if the model is of type Node or Edge, otherwise False.
    """
    if not isinstance(model, NodeModel) and not isinstance(model, EdgeModel):
        return False

    return True


def return_metadatas(
    data: chroma_types.GetResult,
) -> list[dict[str, PrimitiveType]] | None:
    """
    Returns the sanitized metadatas from the ChromaDB collection if they exists and are of the expected
    types, otherwise None.

    Args:
        - `data` (chroma_types.GetResult): The data returned from the ChromaDB collection.

    Returns:
        - `dict[str, PrimitiveType] | None`: The sanitized metadata if it exists, otherwise None.
    """
    if not data:
        logging.warning(f"Data from collection is empty")
        return None

    metadatas: list[dict[str, PrimitiveType]] | None = data["metadatas"]  # type: ignore
    if not metadatas:
        logging.warning(f"Data from collection is empty")
        return None

    return confirm_metadatas(metadatas)


def confirm_metadatas(
    metadatas: list[dict[str, PrimitiveType]]
) -> list[dict[str, PrimitiveType]]:
    """
    Confirms that the metadatas returned from the ChromaDB collection are valid.

    Args:
        - `metadatas` (list[dict[str, PrimitiveType]]): The metadatas returned from the ChromaDB collection.

    Returns:
        - `list[dict[str, PrimitiveType]]`: The metadatas if they are valid.

    Raises:
        - `TypeError`: If the metadatas are not of type `dict`.
        - `KeyError`: If the `vrtx_model_type` key is not found in the metadatas.
    """
    if not all(isinstance(metadata, dict) for metadata in metadatas):
        raise TypeError("Metadatas from ChromaDB collection are not of type `dict`")
    if not all("vrtx_model_type" in metadata for metadata in metadatas):
        raise KeyError(
            "`vrtx_model_type` not found in all metadatas from ChromaDB collection"
        )
    return metadatas


def return_model(data: dict[str, PrimitiveType]) -> NodeModel | EdgeModel:
    """
    Returns a NodeModel or EdgeModel based on the metadata.

    Args:
        - `metadata` (dict[str, PrimitiveType]): The metadata to use to return the model.

    Returns:
        - `NodeModel | EdgeModel`: The model based on the metadata.
    """
    if data["vrtx_model_type"] == "node":
        return NodeModel.deserialize(data)
    elif data["vrtx_model_type"] == "edge":
        return EdgeModel.deserialize(data)
    else:
        raise ValueError(
            f"Expected `vrtx_model_type` to be `node` or `edge`, got {data['vrtx_model_type']} instead"
        )


def update_where_filter(
    table: str | None, where_filter: chroma_types.Where
) -> chroma_types.Where:
    """
    Updates the where filter to include the table name if table is provided.

    Args:
        - `table` (str): The table name.
        - `where_filter` (chroma_types.Where): The where filter.

    Returns:
        - `chroma_types.Where`: The updated where filter.
    """
    if table:
        where_filter["table"] = table
    return where_filter


def ensure_metadatas_in_include(include_list: list[QueryInclude]) -> list[QueryInclude]:
    """
    Appends the `metadatas` to the include list if it is not already included.

    Args:
        - `include_list` (list[QueryInclude]): The include list.

    Returns:
        - `list[QueryInclude]`: The updated include list.
    """
    if QueryInclude.METADATAS not in include_list:
        include_list.append(QueryInclude.METADATAS)
    return include_list


def process_query_return(result: chroma_types.QueryResult) -> list[QueryReturn]:
    """
    Returns a list of QueryReturn objects from the ChromaDB query result.

    Args:
        - `result` (chroma_types.QueryResult): The result from the ChromaDB query.

    Returns:
        - `list[QueryReturn]`: The list of QueryReturn objects.

    Raises:
        - `Exception`: If the ChromaDB query failed to return anything.
    """
    if not result or not result["metadatas"]:
        raise Exception("ChromaDB query failed to return anything")

    # TODO: Refactor to first create a list of dictionaries, extracting all of the connected data from the result and then
    # TODO: create the QueryReturn objects from the list of dictionaries so that the code is more readable.
    query_returns: list[QueryReturn] = []
    for i, metadatas in enumerate(result["metadatas"]):
        for j, data in enumerate(metadatas):
            model: NodeModel | EdgeModel = return_model(data)  # type: ignore
            document: str | None = (
                result["documents"][i][j]
                if result["documents"] and result["documents"][i]
                else None
            )
            embedding: chroma_types.Embedding | None = (
                result["embeddings"][i][j]
                if result["embeddings"] and result["embeddings"][i]
                else None
            )
            distance: float | None = (
                result["distances"][i][j]
                if result["distances"] and result["distances"][i]
                else None
            )
            uri: chroma_types.URI | None = (
                result["uris"][i][j] if result["uris"] and result["uris"][i] else None
            )
            query_return: QueryReturn = QueryReturn(
                model=model,
                document=document,
                embedding=embedding,
                distance=distance,
                uri=uri,
            )
            query_returns.append(query_return)

    return query_returns
