def main() -> None:
    from vertix.models import NodeModel, EdgeModel

    """
    Nodes:

    Nodes are created using the NodeModel class.

    Note: The `additional_attributes` field is a dictionary that can contain any additional attributes you want to store with the node.
    Only primitive types (str, int, float, bool) are supported as values.
    """
    # Create the user nodes.
    user_1 = NodeModel(
        label="User",
        document="Likes sci-fi movies, frequent buyer of tech gadgets",
        additional_attributes={"age": 30, "location": "New York"},
    )
    user_2 = NodeModel(
        label="User",
        document="Enjoys romantic comedies, purchases home decor frequently",
        additional_attributes={"age": 45, "location": "Los Angeles"},
    )

    # Create the movie node.
    # NOTE: The model has a `description` field, if you set it in the `additional_attributes` field, it will appear in the normal field location.
    # NOTE: If you want `description`, or any other field to specific to your use and it does not apply to the standard model fields, use unique names.
    # WARNING: If you use a name in the `additional_attributes` field that is the same as a standard model field, it will overwrite the standard model field.
    movie = NodeModel(
        label="Movie",
        document="Sci-fi genre, high ratings in special effects, post-apocalyptic theme",
        additional_attributes={
            "title'": "The Rabbit Becoming",
            "release_year": 2023,
            "director": "John Doe",
            "description": "Post-apocalypse, carrots are the only crop to survive, evolution drives humans to develop rabbit-like features.",
        },
    )

    # Create the gadget node.
    gadget = NodeModel(
        label="Gadget",
        document="Latest smartphone, high battery life, popular among young adults",
        additional_attributes={"brand": "TechBrand", "price_range": "High"},
    )

    # Create the book node.
    book = NodeModel(
        label="Book",
        document="Romantic comedy genre, best-seller in fiction, popular among the lactose intolerant",
        description="In a world of lactose tolerance, two find love without.",
        additional_attributes={
            "title": "Hold the Cheese",
            "author": "Jane Smith",
            "pages": 350,
        },
    )

    # Create the system node.
    system_node = NodeModel(
        vrtx_model_type="node",
        label="System",
        document="Automated recommendation engine responsible for analyzing user behavior and generating personalized product suggestions.",
        additional_attributes={"type": "Recommendation Engine", "version": "1.0"},
    )

    """
    Edges:

    Edges are created in a similar way to nodes, but with the additional `from_id` and `to_id` fields.

    Note: By default the models created directed edges. To create undirected edges, set the `is_directed` parameter to False.
    """
    # Create the viewed edge.
    viewed_edge = EdgeModel(
        from_id=user_1.id,
        to_id=movie.id,
        document="Watched multiple times, high engagement",
        edge_type="viewed",
    )
    viewed_edge_id: str = viewed_edge.id

    # Create the purchased edge.
    purchased_edge = EdgeModel(
        from_id=user_1.id,
        to_id=gadget.id,
        document="Purchased during sale, positive review",
        edge_type="purchased",
    )

    # Create the browsed edge.
    browsed_edge = EdgeModel(
        from_id=user_2.id,
        to_id=book.id,
        document="Browsed multiple times, added to wishlist",
        edge_type="browsed",
    )

    # Create the rated edge.
    rated_edge = EdgeModel(
        from_id=user_1.id,
        to_id=movie.id,
        document="Rated 5 stars, left a positive review",
        edge_type="rated",
    )

    # Create the recommended edge.
    recommended_edge = EdgeModel(
        from_id=system_node.id,
        to_id=user_2.id,
        document="Recommended based on previous home decor purchases",
        edge_type="recommended",
    )

    from vertix.typings import chroma_types
    from vertix.db import setup_ephemeral_client, ChromaDBHandler, ChromaDB
    from vertix.db import QueryInclude, QueryReturn
    from rich import print

    # Create a ChromaDB client.
    client: chroma_types.ClientAPI = setup_ephemeral_client()

    # Create chromadb collection.
    collection: chroma_types.Collection = ChromaDBHandler(
        client
    ).get_or_create_collection("recommendation_example")

    # Create a ChromaDB instance, the ORM for the chroma_db collection.
    chroma_db: ChromaDB = ChromaDB(collection=collection)

    # Gather all the models.
    nodes: list[NodeModel] = [user_1, user_2, movie, gadget, book, system_node]
    edges: list[EdgeModel] = [
        viewed_edge,
        purchased_edge,
        browsed_edge,
        rated_edge,
        recommended_edge,
    ]
    models: list[NodeModel | EdgeModel] = nodes + edges

    # Add the models to the ChromaDB instance.
    for model in models:
        chroma_db.add(model)

    # Query the whole collection.
    queries: list[str] = ["dark sci-fi", "romantic comedy"]
    query_returns: list[QueryReturn] | None = chroma_db.query(
        queries=queries,
        n_results=2,
        include=[
            QueryInclude.DOCUMENTS,
            QueryInclude.DISTANCES,
            QueryInclude.EMBEDDINGS,
        ],
    )
    if query_returns:
        for i, query_return in enumerate(query_returns):
            print(f"[bold green]Document {i+1}:[/] {query_return.document}")
            print(
                f"[blue]Showing document in model is same as document returned from the query[/]"
            )
            print(f"[bold green]Document {i+1}:[/] {query_return.model.document}")
            print(query_return.model)

    # Query the just just the edges in the collection by setting the `table` parameter to "edges" in the query method.
    query_2 = "positive impression"
    query_returns_2: list[QueryReturn] | None = chroma_db.query(
        queries=[query_2],
        n_results=2,
        table="edges",
        include=[
            QueryInclude.DOCUMENTS,
            QueryInclude.DISTANCES,
            QueryInclude.EMBEDDINGS,
        ],
    )
    if query_returns_2:
        for i, query_return in enumerate(query_returns_2):
            print(f"[bold green]Document {i+1}:[/] {query_return.document}")
            print(f"[blue]Showing document in model is same as document in query[/]")
            print(f"[bold green]Document {i+1}:[/] {query_return.model.document}")
            print(query_return.model)

    # Note how the metadatas didn't need to be added to the query include list because it is included by default and are
    # actually what is used for the 'row's in the 'table's in the Vertix database.


if __name__ == "__main__":
    main()

"""To create nodes and edges for a recommendation system using the provided models, 
we'll consider a scenario where we have products and users as nodes, and interactions 
(like purchases or views) as edges. The document field in both nodes and edges will be critical for vector similarity 
search, which can be leveraged for personalized recommendations based on user behavior and product features.

Here are 10 examples for nodes and edges in a recommendation system:

Nodes
User Node: Represents a user with attributes like preferences, browsing history, etc.

id: "user_001"
vrtx_model_type: "node"
label: "User"
document: "Likes sci-fi movies, frequent buyer of tech gadgets"
additional_attributes: {"age": 30, "location": "New York"}
Product Node (Movie): Represents a movie in a streaming service.

id: "movie_010"
vrtx_model_type: "node"
label: "Movie"
document: "Sci-fi genre, high ratings in special effects"
additional_attributes: {"release_year": 2023, "director": "John Doe"}
Product Node (Tech Gadget): Represents a tech gadget in an e-commerce platform.

id: "gadget_020"
vrtx_model_type: "node"
label: "Gadget"
document: "Latest smartphone, high battery life, popular among young adults"
additional_attributes: {"brand": "TechBrand", "price_range": "High"}
User Node: Another user with different preferences.

id: "user_002"
vrtx_model_type: "node"
label: "User"
document: "Enjoys romantic comedies, purchases home decor frequently"
additional_attributes: {"age": 45, "location": "Los Angeles"}
Product Node (Book): Represents a book in an online bookstore.

id: "book_030"
vrtx_model_type: "node"
label: "Book"
document: "Romantic comedy genre, best-seller in fiction"
additional_attributes: {"author": "Jane Smith", "pages": 350}
Edges
Viewed Edge: Represents a user viewing a movie.

from_id: "user_001"
to_id: "movie_010"
vrtx_model_type: "edge"
document: "Watched multiple times, high engagement"
is_directed: True
edge_type: "viewed"
Purchased Edge: Represents a user purchasing a gadget.

from_id: "user_001"
to_id: "gadget_020"
vrtx_model_type: "edge"
document: "Purchased during sale, positive review"
is_directed: True
edge_type: "purchased"
**

Browsed Edge: Represents a user browsing a book but not purchasing.

from_id: "user_002"
to_id: "book_030"
vrtx_model_type: "edge"
document: "Browsed multiple times, added to wishlist"
is_directed: True
edge_type: "browsed"
Rated Edge: Represents a user rating a movie.

from_id: "user_001"
to_id: "movie_010"
vrtx_model_type: "edge"
document: "Rated 5 stars, left a positive review"
is_directed: True
edge_type: "rated"
Recommended Edge: Represents a system-generated recommendation for a user.

from_id: "system_001"
to_id: "user_002"
vrtx_model_type: "edge"
document: "Recommended based on previous home decor purchases"
is_directed: True
edge_type: "recommended"

In these examples, the document field plays a crucial role in vector similarity search. For users, 
it could include preferences and behaviors, while for products, it could contain features and attributes. 
The document field in edges can describe the nature of the interaction, such as purchase details, viewing habits, 
or ratings, which are essential for building a robust recommendation system."""
