from typing import Literal
from pydantic import (
    Field,
)
from vertix.models.base_graph_entity_model import BaseGraphEntityModel


class EdgeModel(BaseGraphEntityModel["EdgeModel"]):
    """
    Model for an edge in the graph database.

    Attributes:
        - `id` (str): The primary key for the model (defaults to a uuid4)
        - `vrtx_model_type` (Literal["edge"]): The model type.
        - `label` (str): A custom label for the edge (defaults to an empty string)
        - `document` (str): A string used for vector embedding and similarity search or as other information in the graph (defaults to an empty string)
        - `is_directed` (bool): Whether the edge is directed or not (defaults to True)
        - `allow_parallel_edges` (bool): Whether the edge allows parallel edges or not (defaults to False)
        - `from_id` (str): The id of the node that the edge starts from
        - `to_id` (str): The id of the node that the edge ends at
        - `edge_type` (str): The type of edge (defaults to "edge")
        - `additional_attributes` (AttributeDictType): A dictionary of additional attributes (defaults to an empty dictionary)

    Methods:
        - `serialize()`: Serializes the edge into a flattened dictionary with only primitive types.
        - `deserialize(data)`: Deserializes a dictionary into a model instance.

    Notes:
        - Attributes can be updated by setting the attribute to a new value, e.g. `edge.is_directed = False`
            - Pydantic will validate the new value type and raise an error if it is invalid

    Examples:
        ```Python
        from vertix.models import Edge
        # Create an edge with the default values
        edge = Edge(from_id="123", to_id="456", additional_attributes={"example": "example"})

        # Update attribute
        edge.is_directed = False
        # Serialize the edge
        serialized_edge = edge.serialize()
        ```
    """

    vrtx_model_type: Literal["edge"] = Field(
        description="The model type.",
        default="edge",
        frozen=True,
        validate_default=True,
    )
    table: str = Field(
        description="The table name.",
        default="edges",
    )
    label: str = Field(
        description="A custom label for the edge",
        default="",
    )
    from_id: str = Field(
        description="The id of the node that the edge starts from",
    )
    to_id: str = Field(
        description="The id of the node that the edge ends at",
    )
    edge_type: str = Field(
        description="The type of edge",
        default="edge",
    )
    is_directed: bool = Field(
        description="Whether the edge is directed or not, defaults to True",
        default=True,
    )
    allow_parallel_edges: bool = Field(
        description="Whether the edge allows parallel edges or not, defaults to False",
        default=False,
    )
