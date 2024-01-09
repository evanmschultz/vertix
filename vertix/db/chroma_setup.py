import chromadb

from vertix.typings import chroma_types


def setup_ephemeral_client(
    tenant: str = chroma_types.DEFAULT_TENANT,
    database: str = chroma_types.DEFAULT_DATABASE,
) -> chroma_types.ClientAPI:
    """
    Creates an in-memory instance of a ChromaDB client. This is useful for testing and development, but not recommended for
    production use according the the ChromaDB documentation.

    Args:
        - `tenant` (str): The name of the tenant to connect to (default: `DEFAULT_TENANT`, defined in the ChromaDB library)
        - `database` (str): The name of the database to connect to (default: `DEFAULT_DATABASE`, defined in the ChromaDB library)
    """

    return chromadb.EphemeralClient(tenant=tenant, database=database)


def setup_persistent_client(
    path: str = "./chroma",
    tenant: str = chroma_types.DEFAULT_TENANT,
    database: str = chroma_types.DEFAULT_DATABASE,
) -> chroma_types.ClientAPI:
    """
    Creates a persistent instance of a ChromaDB client. This is useful for testing and development, but not recommended for
    production use according the the ChromaDB documentation.

    Args:
        - `path` (str): The path to the directory where the database will be stored (default: `./chroma`)
        - `tenant` (str): The name of the tenant to connect to (default: `DEFAULT_TENANT`, defined in the ChromaDB library)
        - `database` (str): The name of the database to connect to (default: `DEFAULT_DATABASE`, defined in the ChromaDB library)
    """

    return chromadb.PersistentClient(path=path, tenant=tenant, database=database)


def set_up_http_client(
    host: str = "localhost",
    port: str = "8000",
    ssl: bool = False,
    headers: dict[str, str] = {},
) -> chroma_types.ClientAPI:
    """
    Creates a client that connects to a remote Chroma server. This supports many clients connecting to the same server, and is the recommended way to use Chroma in production.

    Args:
        - `host` (str): The hostname of the Chroma server (default: `localhost`)
        - `port` (str): The port of the Chroma server (default: `8000`)
        - `ssl` (bool): Whether to use SSL to connect to the Chroma server (default: `False`)
        - `headers` (dict[str, str]): A dictionary of headers to send to the Chroma server (default: `{}`)
    """

    return chromadb.HttpClient(host=host, port=port, ssl=ssl, headers=headers)
