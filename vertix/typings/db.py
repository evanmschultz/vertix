from dataclasses import dataclass
from enum import Enum
from vertix.models import NodeModel, EdgeModel
import vertix.typings.chroma as chroma_types


class QueryInclude(str, Enum):
    """An enum representing the different types of data that can be included in a ChromaDB query."""

    DOCUMENTS = "documents"
    EMBEDDINGS = "embeddings"
    DISTANCES = "distances"
    URIS = "uris"
    METADATAS = "metadatas"
    # DATA = "data"


@dataclass(frozen=True, kw_only=True)
class QueryReturn:
    """
    A dataclass representing a query return with the model and any additional data requested in the ChromaDB query.

    Attributes:
        - `model` (NodeModel | EdgeModel): The model.
        - `document` (str | None): The document.
        - `embedding` (chroma_types.Embedding | None): The embedding.
        - `distance` (float | None): The distance.
        - `uri` (chroma_types.URI | None): The URI.
        - `data` (bool): Whether to include the data.

    Examples:
        ```Python
        # Run a query and get the results as query returns.
        models: list[NodeModel | EdgeModel] = []
        embeddings: [chroma_types.Embedding] = []
        for query_return in query_returns:
            models.append(query_return.model)
            embeddings.append(query_return.embedding)

        model_1, embedding_1 = models[0], embeddings[0]
        ```
    """

    model: NodeModel | EdgeModel
    document: str | None = None
    embedding: chroma_types.Embedding | None = None
    distance: float | None = None
    uri: chroma_types.URI | None = None
    # data: bool = False
