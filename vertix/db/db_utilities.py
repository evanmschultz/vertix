import logging
from vertix.models import NodeModel, EdgeModel
from vertix.typings import PrimitiveType, chroma_types


# def update(model: NodeModel | EdgeModel, collection: chroma_types.Collection) -> None:
#     """
#     Updates a model in the ChromaDB collection.

#     Args:
#         - `model` (Node | Edge): The model to update in the collection.

#     Raises:
#         - `TypeError`: If the model is not of type Node or Edge.
#         - `Exception`: If the model could not be updated in the collection.
#     """
#     try:
#         model_data: dict[str, PrimitiveType] = model.serialize()
#         collection.update(ids=model.id, documents=model.document, metadatas=model_data)
#     except Exception as e:
#         raise Exception(f"Could not update model with id `{model.id}`: {e}")


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


def return_model(metadata: dict[str, PrimitiveType]) -> NodeModel | EdgeModel:
    """
    Returns a NodeModel or EdgeModel based on the metadata.

    Args:
        - `metadata` (dict[str, PrimitiveType]): The metadata to use to return the model.

    Returns:
        - `NodeModel | EdgeModel`: The model based on the metadata.
    """
    if metadata["vrtx_model_type"] == "node":
        return NodeModel.deserialize(metadata)
    elif metadata["vrtx_model_type"] == "edge":
        return EdgeModel.deserialize(metadata)
    else:
        raise ValueError(
            f"Expected `vrtx_model_type` to be `node` or `edge`, got {metadata['vrtx_model_type']} instead"
        )


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
