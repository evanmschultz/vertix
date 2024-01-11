import chromadb

import vertix.utilities.utilities as utils
from vertix.typings import chroma_types


def setup_ephemeral_client(
    tenant: str = chroma_types.DEFAULT_TENANT,
    database: str = chroma_types.DEFAULT_DATABASE,
) -> chroma_types.ClientAPI:
    """
    Creates a ChromaDB `EphemeralClient` instance, a client that connects to a Chroma database in memory. This is for testing and
    development purposes only and is not recommended for production use.

    Args:
        - `tenant` (str): The tenant of the Chroma database (default: `default_tenant`)
        - `database` (str): The database of the Chroma database (default: `default_database`)

    Returns:
        - `chroma_types.ClientAPI`: The ChromaDB client

    Raises:
        - `TypeError`: If the `tenant` or `database` arguments are not strings
    """

    if not utils.all_are_strings([tenant, database]):
        raise TypeError(
            f"All arguments must be strings. Got types {type(tenant)}, and {type(database)}"
        )

    return chromadb.EphemeralClient(tenant=tenant, database=database)


def setup_persistent_client(
    path: str = "./chroma",
    tenant: str = chroma_types.DEFAULT_TENANT,
    database: str = chroma_types.DEFAULT_DATABASE,
) -> chroma_types.ClientAPI:
    """
    Creates a ChromaDB `PersistentClient` instance, a client that connects to a Chroma database in local long-term storage.
    This is meant for testing and development purposes only and is not recommended for production use according to the ChromaDB
    documentation.

    Args:
        - `path` (str): The path to the Chroma database (default: `./chroma`)
        - `tenant` (str): The tenant of the Chroma database (default: `default_tenant`)
        - `database` (str): The database of the Chroma database (default: `default_database`)

    Returns:
        - `ChromaDBHandler`: The ChromaDB client

    Raises:
        - `TypeError`: If the `path`, `tenant`, or `database` arguments are not strings
    """

    if not utils.all_are_strings([path, tenant, database]):
        raise TypeError(
            f"All arguments must be strings. Got types {type(path)}, {type(tenant)}, and {type(database)}"
        )

    return chromadb.PersistentClient(path=path, tenant=tenant, database=database)


def setup_http_client(
    host: str = "localhost",
    port: str = "8000",
    ssl: bool = False,
    headers: dict[str, str] = {},
) -> chroma_types.ClientAPI:
    """
    Creates a ChromaDB `HttpClient` instance, a client that connects to a remote Chroma server. This is the recommended way to use Chroma
    in production according to the ChromaDB documentation.

    Args:
        - `host` (str): The hostname of the Chroma server (default: `localhost`)
        - `port` (str): The port of the Chroma server (default: `8000`)
        - `ssl` (bool): Whether to use SSL to connect to the Chroma server (default: `False`)
        - `headers` (dict[str, str]): A dictionary of headers to send to the Chroma server (default: `{}`)

    Returns:
        - `ChromaDBHandler`: The ChromaDB client

    Raises:
        - `TypeError`: If the `host` or `port` arguments are not strings
        - `TypeError`: If the `ssl` argument is not a boolean
        - `TypeError`: If the `headers` argument is not a dictionary or `None`
        - `TypeError`: If the `headers` argument has keys that are not strings
        - `TypeError`: If the `headers` argument has values that are not strings
    """

    if not utils.all_are_strings([host, port]):
        raise TypeError(
            f"`host` and `port` arguments must be strings. Got types {type(host)} and {type(port)}"
        )

    if not utils.all_are_bool([ssl]):
        raise TypeError(f"`ssl` argument must be a boolean. Got type {type(ssl)}")

    if not utils.is_dict_str_str(headers) or headers is None:
        raise TypeError(
            f"`headers` argument must be a dictionary with string keys and string values."
        )

    return chromadb.HttpClient(host=host, port=port, ssl=ssl, headers=headers)
