import logging
from vertix.utilities.rich_config import console, setup_logging
from vertix.models import Node, Edge
from vertix.typings import PrimitiveType

if __name__ == "__main__":
    node = Node(id="123", label="test", description="test", type="test")
    console.log(node)
    node.additional_attributes = {"test": False}
    serialized_dict: dict[str, PrimitiveType] = node.serialize()
    console.log(serialized_dict)
    edge = Edge(from_id="123", to_id="123")
    console.log(edge)
    edge.allow_parallel_edges = True
    edge.additional_attributes = {"test": False}
    edge.additional_attributes["test_2"] = 1
    console.log(edge.serialize())
    console.log()
    logging.info("Info")
    logging.debug("Debug")
