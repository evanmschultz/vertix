import logging

import vertix.utilities.utilities as utils
from vertix.typings import chroma_types


class ChromaDBHandler:
    """
    A class for managing the ChromaDB client and its collections.

    Client types:
        - `EphemeralClient`: A client that connects to a Chroma database in memory. This is for testing and development purposes only and
            is not recommended for production use.
        - `PersistentClient`: A client that connects to a Chroma database in local long-term storage. This is meant for testing and
            development purposes only and is not recommended for production use according to the ChromaDB documentation.
        - `HttpClient`: A client that connects to a remote Chroma server. This is the recommended way to use Chroma in production according
            to the ChromaDB documentation.

    Methods:
        - `get_or_create_collection`: Gets or creates a collection with the given name, metadata, and embeddings function.
        - `delete_collection`: Deletes a collection with the given name.
        - `reset_client`: Resets the client, deleting all collections and documents.

    Examples:
        ```Python
        from vertix.db import ChromaDBHandler, setup_ephemeral_client

        # Setup a ChromaDB client
        client = setup_ephemeral_client()
        chroma_client = ChromaDBHandler(client)

        # Get or create a collection
        collection = chroma_client.get_or_create_collection("test_collection")
        ```

    Notes:
        - For more information on the ChromaDB library and what different methods can do see the ChromaDB documentation:
            https://docs.trychroma.com/
    """

    def __init__(self, client: chroma_types.ClientAPI) -> None:
        self.client: chroma_types.ClientAPI = client

    def get_or_create_collection(
        self,
        name: str,
        metadata: chroma_types.CollectionMetadata | None = None,
        embedding_function: chroma_types.EmbeddingFunction
        | None = chroma_types.ef.DefaultEmbeddingFunction(),
    ) -> chroma_types.Collection:
        """
        Gets or creates a collection with the given name, metadata, and embeddings function.

        Args:
            - `name` (str): The name of the collection to get or create
            - `metadata` (chroma_types.CollectionMetadata | None): Optional metadata to associate with the collection
            - `embedding_function` (chroma_types.ef.EmbeddingFunction | None): Optional function to use to embed documents

        Returns:
            - `chroma_types.Collection`: The ChromaDB collection used as a database or table in a database in Vertix

        Raises:
            - `TypeError`: If the `name` argument is not a `str`
            - `TypeError`: If the `metadata` argument is not a `chroma_types.CollectionMetadata` or `None`
                - `chroma_types.CollectionMetadata` is `dict[str, Any]`

        Notes:
            - For more information on embedding functions, and which are allowed, see the ChromaDB documentation:
                https://docs.trychroma.com/embeddings
        """
        if not isinstance(name, str):
            raise TypeError(f"`name` argument must be a string. Got type {type(name)}")

        if not isinstance(metadata, dict) and metadata is not None:
            raise TypeError(
                f"`metadata` argument must be a chroma_types.CollectionMetadata (dict[str, Any]) or None. Got type {type(metadata)}"
            )

        return self.client.get_or_create_collection(
            name=name, metadata=metadata, embedding_function=embedding_function
        )

    def delete_collection(self, name: str) -> None:
        """
        Deletes a collection with the given name.

        Args:
            - `name` (str): The name of the collection to delete

        Raises:
            - `Exception`: If the collection could not be deleted
        """
        if not isinstance(name, str):
            raise TypeError(f"`name` argument must be a string. Got type {type(name)}")

        self.client.delete_collection(name=name)

    def reset_client(self) -> None:
        """
        Resets the client, deleting all collections and documents.

        Raises:
            - `Exception`: If the client could not be reset
        """
        client_reset: bool = self.client.reset()

        if not client_reset:
            raise Exception("Client reset failed")

        logging.info("Client reset successful")
