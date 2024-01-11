import logging

from vertix.models import Node, Edge
from vertix.typings import PrimitiveType
import vertix.typings.chroma as chroma_types


class ChromaDB:
    """
    Wrapper class for a ChromaDB collection, works as the interface between Vertix and your ChromaDB collection.

    Attributes:
        - `chroma_client` (chroma_types.ClientAPI): The ChromaDB client to use.
        - `collection` (chroma_types.Collection): The ChromaDB collection to use.

    Methods:
        - `add_node`: Adds a node to the ChromaDB collection.
        - `get_node`: Gets a node from the ChromaDB collection.
        - `add_edge`: Adds an edge to the ChromaDB collection.
        - `get_edge`: Gets an edge from the ChromaDB collection.

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
    """

    def __init__(
        self, chroma_client: chroma_types.ClientAPI, collection: chroma_types.Collection
    ) -> None:
        self.chroma_client: chroma_types.ClientAPI = chroma_client
        self.collection: chroma_types.Collection = collection

    def add_node(self, node: Node) -> None:
        """
        Adds a node to the ChromaDB collection.

        Args:
            - `node` (Node): The node model to add to the collection.

        Raises:
            - `TypeError`: If the node is not of type Node.
            - `Exception`: If the node could not be added to the collection.
        """
        if not self._validate_node_type(node):
            raise TypeError(
                f"Expected node to be of type Node, got {type(node)} instead"
            )

        try:
            self._add(node)
        except Exception as e:
            raise e

    def get_node(self, id) -> Node | None:
        """
        Gets a node from the ChromaDB collection.

        Args:
            - `id` (str): The id of the node to get from the collection.

        Returns:
            - `Node | None`: The node if it exists, otherwise None (will log a warning if the `id`
                was not found in the collection).

        Raises:
            - `TypeError`: If the node is not of type Node.
            - `Exception`: If the node could not be added to the collection.
        """
        data: chroma_types.GetResult = self.collection.get(id)
        if not data:
            logging.warning(f"Node with id `{id}` not found")
            return None

        metadatas: list[chroma_types.Metadata] | None = data["metadatas"]
        if not metadatas:
            logging.warning(f"Node with id `{id}` not found")
            return None

        metadata = metadatas[0]
        if not isinstance(metadata, dict):
            raise TypeError(
                f"Expected metadata from ChromaDB to be a dict, got {type(metadata)} instead"
            )
        return Node.deserialize(metadata)

    def add_edge(self, edge: Edge) -> None:
        """
        Adds an edge to the ChromaDB collection.

        Args:
            - `edge` (Edge): The edge model to add to the collection.

        Raises:
            - `TypeError`: If the edge is not of type Edge.
            - `Exception`: If the edge could not be added to the collection.
        """
        if not self._validate_edge_type(edge):
            raise TypeError(
                f"Expected edge to be of type Edge, got {type(edge)} instead"
            )

        try:
            self._add(edge)
        except Exception as e:
            raise e

    def get_edge(self, id) -> Edge | None:
        """
        Gets an edge from the ChromaDB collection.

        Args:
            - `id` (str): The id of the edge to get from the collection.

        Returns:
            - `Edge | None`: The edge if it exists, otherwise None (will log a warning if the `id`
                was not found in the collection).

        Raises:
            - `TypeError`: If the edge is not of type Edge.
            - `Exception`: If the edge could not be added to the collection.
        """
        data: chroma_types.GetResult = self.collection.get(id)
        if not data:
            logging.warning(f"Edge with id `{id}` not found")
            return None

        metadatas: list[chroma_types.Metadata] | None = data["metadatas"]
        if not metadatas:
            logging.warning(f"Edge with id `{id}` not found")
            return None

        metadata = metadatas[0]
        if not isinstance(metadata, dict):
            raise TypeError(
                f"Expected metadata from ChromaDB to be a dict, got {type(metadata)} instead"
            )
        return Edge.deserialize(metadata)

    # def update_node(self, id, data):
    #     # Use ChromaDB's functionality to update a node
    #     self.chroma_client.update_node(id, data)

    # def delete_node(self, id):
    #     # Use ChromaDB's functionality to delete a node
    #     self.chroma_client.delete_node(id)

    def _add(self, model: Node | Edge) -> None:
        """
        Adds a model to the ChromaDB collection.

        Args:
            - `model` (Node | Edge): The model to add to the collection.

        Raises:
            - `TypeError`: If the model is not of type Node or Edge.
            - `Exception`: If the model could not be added to the collection.
        """
        try:
            model_data: dict[str, PrimitiveType] = model.serialize()
            self.collection.add(
                ids=model.id, documents=model.document, metadatas=model_data
            )
        except Exception as e:
            raise e

    def _validate_node_type(self, node: Node) -> bool:
        """
        Validates that the node is of type Node.

        Args:
            - `node` (Node): The node to validate.

        Returns:
            `bool`: True if the node is of type Node, otherwise False.
        """
        return isinstance(node, Node)

    def _validate_edge_type(self, edge: Edge) -> bool:
        """
        Validates that the edge is of type Edge.

        Args:
            - `edge` (Edge): The edge to validate.

        Returns:
            `bool`: True if the edge is of type Edge, otherwise False.
        """
        return isinstance(edge, Edge)