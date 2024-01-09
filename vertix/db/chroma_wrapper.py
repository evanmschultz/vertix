import logging

from vertix.models import Node, Edge
from vertix.typings import PrimitiveType

import vertix.typings.chroma as chroma


class ChromaDBWrapper:
    def __init__(self, chroma_client: chroma.ClientAPI, collection_name: str) -> None:
        self.chroma_client: chroma.ClientAPI = chroma_client
        self.collection: chroma.Collection = chroma_client.get_or_create_collection(
            collection_name
        )

    def add_node(self, node: Node) -> None:
        try:
            node_data: dict[str, PrimitiveType] = node.serialize()
            self.collection.add(
                ids=node.id, documents=node.document, metadatas=node_data
            )
        except Exception as e:
            raise e

    def get_node(self, id) -> Node | None:
        data: chroma.GetResult = self.collection.get(id)
        if not data:
            logging.warning(f"Node with id {id} not found")
            return None

        metadatas: list[chroma.Metadata] | None = data["metadatas"]

        if not metadatas:
            logging.warning(f"Node with id {id} not found")
            return None
        else:
            metadata = metadatas[0]

            if not isinstance(metadata, dict):
                raise TypeError(
                    f"Expected metadata to be a dict, got {type(metadata)} instead"
                )

            return Node.deserialize(metadata)

    # def update_node(self, id, data):
    #     # Use ChromaDB's functionality to update a node
    #     self.chroma_client.update_node(id, data)

    # def delete_node(self, id):
    #     # Use ChromaDB's functionality to delete a node
    #     self.chroma_client.delete_node(id)

    # def create_edge(self, source_id, target_id, data):
    #     # Use ChromaDB's functionality to create an edge
    #     edge_id = self.chroma_client.create_edge(source_id, target_id, data)
    #     return Edge(source_id, target_id, data)

    # ... and so on for other operations
