from datetime import datetime
import uuid

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from vertix.typings import (
    AttributeDictType,
    PrimitiveType,
)


class BaseGraphEntityModel(BaseModel, validate_assignment=True):
    """
    A base class for models to be used in the ORM for the graph databases.

    Attributes:
        - id (str): The primary key for the the model, used to create edges (defaults to a uuid4)
        - label (str): A custom label for the node (defaults to an empty string)
        - description (str): A description of the node (defaults to an empty string)
        - type (str): The type of node, used to create edges (defaults to "node")
        - neighbors_count (int): The number of neighbors this node has (defaults to 0)
        - created_at (str): The time at creation (defaults to the current time)
        - updated_at (str): The time at the last update (defaults to the current time)
        - Extras (PrimitiveType): Any additional attributes assigned to the model


    Methods:
        - `serialize()`: Serializes the node into a flattened dictionary with only primitive types.
    """

    id: str = Field(
        description="The primary key.",
        default_factory=lambda: str(uuid.uuid4()),
    )
    label: str = Field(
        description="A custom label for the model.",
        default="",
    )
    created_at: str = Field(
        description="The time at creation",
        default_factory=lambda: BaseGraphEntityModel._current_time(),
    )
    updated_at: str = Field(
        description="The time at the last update",
        default_factory=lambda: BaseGraphEntityModel._current_time(),
    )
    additional_attributes: AttributeDictType = Field(
        description="A dictionary of additional attributes. Values must be primitive types.",
        default_factory=dict,
    )

    @staticmethod
    def _current_time() -> str:
        """Returns the current timestamp in isoformat"""
        return datetime.utcnow().isoformat()

    @field_validator("additional_attributes", mode="before")
    @classmethod
    def _validate_additional_attributes(cls, v: AttributeDictType) -> AttributeDictType:
        """Validates the additional attributes field"""
        if not isinstance(v, dict):
            raise TypeError("`additional_attributes` must be a dictionary")
        for key, value in v.items():
            if not isinstance(key, str):
                raise TypeError("`additional_attributes` keys must be strings")
            if not isinstance(value, (str, int, float, bool)):
                raise TypeError(
                    "`additional_attributes` values must be strings, ints, floats, or booleans"
                )
        return v

    def serialize(self) -> dict[str, PrimitiveType]:
        """
        Serializes the node into a flattened dictionary with only primitive types.

        Returns:
            - dict[str, PrimitiveType]: A dictionary of the node's attributes
        """

        try:
            self.updated_at = self._current_time()
            return {
                **self.model_dump(exclude={"additional_attributes"}),
                **self.additional_attributes,
            }

        except Exception as e:
            raise e


class Node(BaseGraphEntityModel):
    """
    Model for a node in the graph database.

    Attributes:
        - id (str): The primary key for the the model, used to create edges (defaults to a uuid4)
        - label (str): A custom label for the node (defaults to an empty string)
        - description (str): A description of the node (defaults to an empty string)
        - type (str): The type of node, used to create edges (defaults to "node")
        - neighbors_count (int): The number of neighbors this node has (defaults to 0)
        - additional_attributes (AttributeDictType): A dictionary of additional attributes (defaults to an empty dictionary)

    Methods:
        - `serialize()`: Serializes the node into a flattened dictionary with only primitive types.

    Notes:
        - Attributes can be updated by setting the attribute to a new value, e.g. `node.neighbors_count = 2`
            - Pydantic will validate the new value type and raise an error if it is invalid

    Examples:
        ```Python
        from vertix.models import Node
        # Create a node with the default values
        node = Node(id="123", additional_attributes={"example": "example"})

        # Update attribute
        node.neighbors_count = 2
        # Serialize the node
        serialized_node = node.serialize()
        ```
    """

    description: str = Field(
        description="A description of the node",
        default="",
    )
    type: str = Field(
        description="The type of node, used to create edges",
        default="node",
    )
    neighbors_count: int = Field(
        description="The number of neighbors this node has",
        default=0,
    )


class Edge(BaseGraphEntityModel):
    """
    Model for an edge in the graph database.

    Attributes:
        - id (str): The primary key for the model (defaults to a uuid4)
        - label (str): A custom label for the edge (defaults to an empty string)
        - is_directed (bool): Whether the edge is directed or not (defaults to True)
        - allow_parallel_edges (bool): Whether the edge allows parallel edges or not (defaults to False)
        - from_id (str): The id of the node that the edge starts from
        - to_id (str): The id of the node that the edge ends at
        - type (str): The type of edge (defaults to "edge")
        - additional_attributes (AttributeDictType): A dictionary of additional attributes (defaults to an empty dictionary)

    Methods:
        - `serialize()`: Serializes the edge into a flattened dictionary with only primitive types.

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

    from_id: str = Field(
        description="The id of the node that the edge starts from",
    )
    to_id: str = Field(
        description="The id of the node that the edge ends at",
    )
    type: str = Field(
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
