import logging
from uuid import uuid4

from rich import print
from pydantic import BaseModel
from vertix.db.hylladb.model_generator.auto_generate_models import (
    create_subset_models,
    write_code_to_file,
    User,
    HyllaBaseModel,
)
from vertix.utilities.rich_config import console, setup_logging
from vertix.models import NodeModel, EdgeModel
from vertix.typings import PrimitiveType

# if __name__ == "__main__":
#     node = NodeModel(id="123", label="test", description="test", node_type="test")
#     console.log(node)
#     node.additional_attributes = {"test": False}
#     serialized_dict: dict[str, PrimitiveType] = node.serialize()
#     console.log(serialized_dict)
#     edge = EdgeModel(from_id="123", to_id="123")
#     console.log(edge)
#     edge.allow_parallel_edges = True
#     edge.additional_attributes = {"test": False}
#     edge.additional_attributes["test_2"] = 1
#     console.log(edge.serialize())
#     console.log()
#     logging.info("Info")
#     logging.debug("Debug")

if __name__ == "__main__":
    # Generate subset models for User
    subset_models: list[type[BaseModel]] = create_subset_models(User)

    print(f"Number of subset models generated: {len(subset_models)}\n")

    for model in subset_models:
        model_instance = model(id=uuid4(), name="John", email="", age=HyllaBaseModel())
        print(f"Model: {model.__name__}")
        print(f"\n{model.__doc__}\n")
        for field_name, field_type in model.__annotations__.items():
            print(f"    {field_name}: {field_type.__name__}")
        print("\n")
        print(model_instance.model_dump_json(indent=4))
        print("\n")
        print(model.__module__)
        print("\n")

    write_code_to_file(subset_models)
