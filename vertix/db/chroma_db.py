import logging
from vertix.models import NodeModel, EdgeModel
import vertix.db.db_utilities as db_utils

from vertix.typings.db import QueryInclude, QueryReturn
from vertix.typings import PrimitiveType, chroma_types


class ChromaDB:
    """
    Wrapper class for a ChromaDB collection, works as the interface for the "database" (ChromaDB collection).

    Attributes:
        - `chroma_client` (chroma_types.ClientAPI): The ChromaDB client to use.
        - `collection` (chroma_types.Collection): The ChromaDB collection to use.

    Methods:
        - `add`: Adds a model (`NodeModel | EdgeModel`) to the ChromaDB collection.
        - `get_by_id`: Gets a model (`NodeModel | EdgeModel`) from the ChromaDB collection by its ID.
        - `update`: Updates a model (`NodeModel | EdgeModel`) in the ChromaDB collection by its ID.
        - `delete_by_id`: Deletes a 'node' or 'edge' from the ChromaDB collection.
        - `delete_by_where_filter`: Deletes a 'node' or 'edge' from the ChromaDB collection.
        - `query`: Gets the n_results (int) nearest neighbor embeddings for provided query from the database.

    Examples:
        ```Python
        from vertix.db import ChromaDBHandler
        import vertix.db as setup_client
        from vertix.db import ChromaDB
        # Setup a ChromaDB client
        client = setup_client.setup_ephemeral_client()
        chroma_client = ChromaDBHandler(client)
        # Get or create a collection
        collection = chroma_client.get_or_create_collection("test_collection")
        # Create a ChromaDB wrapper for the collection
        chroma_db = ChromaDB(chroma_client, collection)
        ```

    Notes:
        This class is a wrapper for the ChromaDB collection logic, making sure it works as Vertix expects it to. If
        there are any ChromaDB features or functionalities you would like to see added, please open an issue on the Vertix
        GitHub repo: https://github.com/evanmschultz/vertix.git
    """

    def __init__(
        self, chroma_client: chroma_types.ClientAPI, collection: chroma_types.Collection
    ) -> None:
        self.chroma_client: chroma_types.ClientAPI = chroma_client
        self.collection: chroma_types.Collection = collection

    def add(self, model: NodeModel | EdgeModel) -> None:
        """
        Adds a model to the ChromaDB collection.

        Args:
            - `model` (Node | Edge): The model to add to the collection.

        Raises:
            - `TypeError`: If the model is not of type Node or Edge.
            - `Exception`: If the model could not be added to the collection.

        Examples:
            ```Python
            from vertix import NodeModel
            # Create a NodeModel
            node = NodeModel(document="Test Document")
            # Add the NodeModel to the collection
            chroma_db.add(node)
            ```
        """
        if not db_utils.validate_model_type(model):
            raise TypeError(
                f"Expected model to be of type `NodeModel` or `EdgeModel`, got {type(model)} instead"
            )

        try:
            model_data: dict[str, PrimitiveType] = model.serialize()
            self.collection.add(
                ids=model.id, documents=model.document, metadatas=model_data
            )
        except Exception as e:
            raise e

    def get_by_id(self, id) -> NodeModel | EdgeModel | None:
        """
        Gets a model from the ChromaDB collection by its ID.

        Args:
            - `id` (str): The id of the node to get from the collection.

        Returns:
            - `NodeModel | EdgeModel | None`: The model if the id exists in the collection, otherwise None (will log a warning if
                the `id` was not found in the collection).

        Raises:
            - `TypeError`: If the metadata returned from the ChromaDB collection is not a dict.
            - `KeyError`: If the `vrtx_model_type` key is not found in the metadata.
            - `ValueError`: If the `vrtx_model_type` value is not `node` or `edge`.

        Examples:
            ```Python
            # Get the NodeModel from the collection
            node_from_db = chroma_db.get_by_id("node_id")
            ```
        """
        data: chroma_types.GetResult = self.collection.get(id)
        metadatas: list[dict[str, PrimitiveType]] | None = db_utils.return_metadatas(
            data
        )

        if not metadatas:
            return None
        return db_utils.return_model(metadatas[0])

    def get_all(self) -> list[NodeModel | EdgeModel] | None:
        """
        Gets all models from the ChromaDB collection.

        Returns:
            - `list[NodeModel | EdgeModel]`: A list of all models in the collection.

        Raises:
            - `TypeError`: If the metadata returned from the ChromaDB collection is not a dict.
            - `KeyError`: If the `vrtx_model_type` key is not found in the metadata.
            - `ValueError`: If the `vrtx_model_type` value is not `node` or `edge`.

        Examples:
            ```Python
            # Get all NodeModels from the collection
            nodes_from_db = chroma_db.get_all()
            ```
        """
        data: chroma_types.GetResult = self.collection.get()
        if not data:
            logging.warning("Collection's `data` is non-existent")
            return None

        metadatas: list[chroma_types.Metadata] | None = data["metadatas"]
        if not metadatas:
            logging.warning("Collection's `metadatas` empty")
            return None

        models: list[NodeModel | EdgeModel] = []
        for metadata in metadatas:
            models.append(db_utils.return_model(metadata))  # type: ignore

        return models

    def update(self, model: NodeModel | EdgeModel) -> None:
        """
        Updates a model in the ChromaDB collection by its ID.

        Args:
            - `model` (Node | Edge): The model to update in the collection.

        Raises:
            - `TypeError`: If the model is not of type Node or Edge.
            - `Exception`: If the model could not be updated in the collection.

        Examples:
            ```Python
            # Update the NodeModel and update it in the collection
            node.document = "Updated Document"
            chroma_db.update(node)
            ```

        Notes:
            - The `created_at` attribute of the model will be set to the value in the collection and the `updated_at` attribute
                will be set to the current time. Do not set these attributes yourself.
        """
        if not db_utils.validate_model_type(model):
            raise TypeError(
                f"Expected model to be of type `NodeModel` or `EdgeModel`, got {type(model)} instead"
            )
        db_model: NodeModel | EdgeModel | None = self.get_by_id(model.id)
        if not db_model:
            return None

        model.created_at = db_model.created_at
        try:
            model_data: dict[str, PrimitiveType] = model.serialize()
            self.collection.update(
                ids=model.id, documents=model.document, metadatas=model_data
            )
        except Exception as e:
            raise Exception(f"Could not update model with id `{model.id}`: {e}")

    def delete_by_id(self, id: str) -> None:
        """
        Deletes a node or edge from the ChromaDB collection.

        Args:
            - `id` (str): The id of the node or edge to delete.

        Raises:
            - `Exception`: If the node or edge could not be deleted.
        """
        try:
            self.collection.delete([id])
        except Exception as e:
            raise e

    def delete_by_where_filter(self, where: chroma_types.Where) -> None:
        """
        Deletes a node or edge from the ChromaDB collection.

        Args:
            - `where` (chroma_types.Where): The filter to use to delete the node or edge.
                - `where` is a type[Dict[str, str | int | float | bool | Dict[Literal['$gt',
                    '$gte', '$lt', '$lte', '$ne', '$eq', '$and', '$or'], str | int | float
                    | bool] | Dict[Literal['$in', '$nin'], List[str | int | float | bool]]
                    | List[Where]]]
                - For more information on the `where` filter, see the ChromaDB docs:
                    - https://docs.trychroma.com/reference/Collection

        Raises:
            - `Exception`: If the node or edge could not be deleted.
        """
        try:
            self.collection.delete(where=where)
        except Exception as e:
            raise e

    def query(
        self,
        queries: list[str],
        table: str | None = None,
        n_results: int = 10,
        where: chroma_types.Where = {},
        where_document: chroma_types.WhereDocument | None = None,
        include: list[QueryInclude] = [QueryInclude.METADATAS],
    ) -> list[QueryReturn] | None:
        """
        For the provided queries, gets the n_results (int) nearest neighbor documents from the database. The results will be returned as
        a list of `QueryReturn` objects.

        This method allows you to specify what additional data you want returned with the results by passing in a list of the `QueryInclude`
        enum. `QueryInclude.METADATAS` is always included as it is what the models use and as such so is `QueryInclude.DOCUMENTS`. Additional
        options: [`QueryInclude.EMBEDDINGS`, `QueryInclude.DISTANCES`, `QueryInclude.URIS`].

        Args:
            - `queries` (list[str]): The queries to get the closest neighbors of.
            - `table` (str): The table in the collection to query. (defaults to `None`, so the whole collection will be queried).
            - `n_results` (int): The number of neighbors to return for each query. (defaults to `10`).
                - Note: This can return duplicates
            - `where` (chroma_types.Where): A Where type dict used to filter results by. E.g. `{"neighbors_count" : 2, "node_type": "class"}`.
                (defaults to `None`).
            - `where_document` (chroma_types.WhereDocument): A WhereDocument type dict used to filter by what is in the documents. E.g.
                `{$contains: {"text": "hello"}}`. (defaults to `None`).
            - `include` (list[QueryInclude]): A list of what to include in the results. Can contain
                "embeddings", "metadatas", "documents", "distances", "uris". (defaults to `METADATAS`).
                - `METADATAS` are always included as they are what the models use.
                    - Note: `DOCUMENTS` are always included in the `METADATAS` and thus the models.

        Returns:
            - `list[QueryReturn]`: A list of `QueryReturn` dataclasses containing the results.
                - `QueryReturn` is a dataclass that contains the following attributes:
                    - `model` (NodeModel | EdgeModel): The model returned from the query.
                    - `document` (str | None): The document returned from the query.
                    - `embedding` (chroma_types.Embedding | None): The embedding returned from the query.
                    - `distance` (float | None): The distance returned from the query.
                    - `uri` (chroma_types.URI | None): The uri returned from the query.

        Raises:
            - `Exception`: If the query failed to return anything.

        Examples:
            ```Python
            # Get the 10 closest neighbors of the provided query as QueryReturn dataclasses
            query_returns = chroma_db.query(["Test query"])
            # Extract the model from the first QueryReturn object
            model = query_returns[0].model
            ```
        """
        where_filter: chroma_types.Where = db_utils.update_where_filter(table, where)  # type: ignore
        include_list: list[QueryInclude] = db_utils.ensure_metadatas_in_include(include)

        try:
            result: chroma_types.QueryResult = self.collection.query(
                query_texts=queries,
                n_results=n_results,
                where=where_filter,
                where_document=where_document,
                include=include_list,  # type: ignore
            )

            return db_utils.process_query_return(result)
        except Exception as e:
            raise Exception(f"Query failed: {e}")
