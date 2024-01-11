from pydantic import Field


from vertix.models.base_graph_entity_model import BaseGraphEntityModel
from vertix.typings import PrimitiveType


class Node(BaseGraphEntityModel["Node"]):
    """
    Model for a node in the graph database.

    Attributes:
        - `id` (str): The primary key for the the model, used to create edges (defaults to a uuid4)
        - `label` (str): A custom label for the node (defaults to an empty string)
        - `document` (str): A string used for vector embedding and similarity search or as other information in the graph (defaults to an empty string)
        - `description` (str): A description of the node (defaults to an empty string)
        - `type` (str): The type of node, used to create edges (defaults to "node")
        - `neighbors_count` (int): The number of neighbors this node has (defaults to 0)
        - `additional_attributes` (AttributeDictType): A dictionary of additional attributes (defaults to an empty dictionary)

    Methods:
        - `serialize()`: Serializes the node into a flattened dictionary with only primitive types.
        - `deserialize(data)`: Deserializes a dictionary into a model instance.

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
    node_type: str = Field(
        description="The type of node, used to create edges",
        default="node",
    )
    neighbors_count: int = Field(
        description="The number of neighbors this node has",
        default=0,
        ge=0,
    )
