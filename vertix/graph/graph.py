from typing import Iterator

import networkx as networkx
from networkx import Graph as NetworkXGraph
from pydantic import BaseModel, Json

from vertix.models import NodeModel, EdgeModel


class VertixGraph(NetworkXGraph, BaseModel, validate_assignment=True):
    models: list[NodeModel | EdgeModel]
    graph_attributes: dict[str, Json] | None = None

    def __init__(
        self,
        models: list[NodeModel | EdgeModel],
        graph_attributes: dict[str, Json] | None = None,
    ) -> None:
        BaseModel.__init__(self, models=models, graph_attributes=graph_attributes)
        NetworkXGraph.__init__(
            self, None, **graph_attributes if graph_attributes else {}
        )
        self._build_graph(self.models)

    def add_node(self, node: NodeModel) -> None:
        """
        Adds a node to the graph.

        Args:
            - `node` (NodeModel): The node to add to the graph.

        Raises:
            - `TypeError`: If the node is not an instance of `NodeModel`.
        """
        if not isinstance(node, NodeModel):
            raise TypeError(
                f"Expected node to be of type `NodeModel`, got {type(node)} instead"
            )
        super().add_node(node.id, **node.serialize())

    def add_edge(self, edge: EdgeModel) -> None:
        """
        Adds an edge to the graph using.

        Args:
            - `edge` (EdgeModel): The edge to add to the graph.
        """
        super().add_edge(edge.from_id, edge.to_id, **edge.serialize())

    def remove_node(self, node_id: str) -> None:
        """Removes a node from the graph."""
        super().remove_node(node_id)

    def remove_edge(self, from_id: str, to_id: str) -> None:
        """Removes an edge from the graph."""
        super().remove_edge(from_id, to_id)

    def find_node(self, node_id: str) -> NodeModel:
        """
        Retrieves a node from the graph and returns a `NodeModel`.

        Args:
            - `node_id` (str): The node id.

        Returns:
            - `NodeModel`: The node.
        """
        node_from_graph = super().nodes[node_id]
        return NodeModel.deserialize(node_from_graph)

    def find_edge(self, from_id: str, to_id: str) -> EdgeModel:
        """
        Retrieves an edge from the graph and returns an `EdgeModel`.

        Args:
            - `from_id` (str): The from node id.
            - `to_id` (str): The to node id.

        Returns:
            - `EdgeModel`: The edge.
        """
        edge_from_graph = super().edges[from_id, to_id]
        return EdgeModel.deserialize(edge_from_graph)

    def neighbors_ids(self, node_id: str) -> list[str]:
        """
        Returns a list of node ids for all neighbors of the specified node.

        Args:
            - `node_id` (str): The node id.

        Returns:
            - `list[str]`: A list of node ids for all neighbors of the specified node.
        """
        return super().neighbors(node_id)

    def neighbors(self, node_id: str) -> list[NodeModel]:
        """
        Returns a list of NodeModel instances for all neighbors of the specified node.

        Args:
            - `node_id` (str): The node id.

        Returns:
            - `list[NodeModel]`: A list of NodeModel instances for all neighbors of the specified node.
        """
        return [self.find_node(node) for node in super().neighbors(node_id)]

    def iter_neighbors(self, node_id: str) -> Iterator[NodeModel]:
        """
        Returns an iterator of NodeModel instances for all neighbors of the specified node.

        Args:
            - `node_id` (str): The node id.

        Returns:
            - `Iterator[NodeModel]`: An iterator of NodeModel instances for all neighbors of the specified node.
        """
        for node in super().neighbors(node_id):
            yield self.find_node(node)

    def _build_graph(self, models: list[NodeModel | EdgeModel] | None = None) -> None:
        """
        Builds the graph from a list of models.

        Args:
            - `models` (list[NodeModel | EdgeModel]): The list of models.
        """
        if models is None:
            models = self.models

        if not all(
            isinstance(model, (NodeModel, EdgeModel)) for model in models
        ) or not all(model.vrtx_model_type in ("node", "edge") for model in models):
            raise TypeError(
                "Expected models to be a list of `NodeModel` or `EdgeModel` instances."
            )

        for model in models:
            if model.vrtx_model_type == "node":
                self.add_node(model)
            elif model.vrtx_model_type == "edge":
                self.add_edge(model)
            else:
                raise TypeError(
                    f"Expected model to be of type `NodeModel` or `EdgeModel`, got {type(model)} instead"
                )


graph: VertixGraph = VertixGraph(
    models=[
        NodeModel(label="1"),
        NodeModel(label="2"),
        NodeModel(label="3"),
    ]
)

from pydantic import BaseModel


# Define a Pydantic model
class UserData(BaseModel):
    name: str
    role: str
    language: str


# Example data
data = UserData(name="Evan", role="Software Engineer", language="Python")

# Serialize data to JSON string using Pydantic
json_string: str = data.model_dump_json()

# Encode this string to bytes
byte_data: bytes = json_string.encode("utf-8")

# Write byte data to a binary file
with open("data.bin", "wb") as file:
    file.write(byte_data)

# To read back from the file
with open("data.bin", "rb") as file:
    byte_data_read: bytes = file.read()
    json_string_read: str = byte_data_read.decode("utf-8")
    data_read: UserData = UserData.model_validate_json(json_string_read)

print(data_read)
