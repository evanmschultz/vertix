import logging
from vertix.utilities.rich_config import console, setup_logging
from vertix.models import NodeModel, EdgeModel
from vertix.typings import PrimitiveType

if __name__ == "__main__":
    node = NodeModel(id="123", label="test", description="test", node_type="test")
    console.log(node)
    node.additional_attributes = {"test": False}
    serialized_dict: dict[str, PrimitiveType] = node.serialize()
    console.log(serialized_dict)
    edge = EdgeModel(from_id="123", to_id="123")
    console.log(edge)
    edge.allow_parallel_edges = True
    edge.additional_attributes = {"test": False}
    edge.additional_attributes["test_2"] = 1
    console.log(edge.serialize())
    console.log()
    logging.info("Info")
    logging.debug("Debug")
