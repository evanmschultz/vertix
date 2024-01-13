from enum import Enum
from dataclasses import dataclass
from typing import Literal

from vertix.models import NodeModel, EdgeModel
import vertix.typings.chroma as chroma_types


class Include(str, Enum):
    DOCUMENTS = "documents"
    EMBEDDINGS = "embeddings"
    DISTANCES = "distances"
    URIS = "uris"
    # METADATAS = "metadatas"
    # DATA = "data"


@dataclass
class QueryReturn:
    models: list[NodeModel | EdgeModel]
    documents: list[str] | Literal[False] = False
    embeddings: list[chroma_types.Embedding] | Literal[False] = False
    distances: list[list[float]] | Literal[False] = False
    uris: list[list[chroma_types.URI]] | Literal[False] = False
    # data: bool = False
