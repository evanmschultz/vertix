from vertix.typings import PrimitiveType


def all_are_strings(args: list) -> bool:
    """
    Checks if all elements in a list are strings.

    Args:
        - `list` (list): The list to check

    Returns:
        - `bool`: True if all elements are strings, False otherwise
    """
    if not isinstance(args, list):
        raise TypeError(f"`list` argument must be a list. Got type {type(list)}")

    return all(isinstance(arg, str) for arg in args)


def all_are_bool(args: list) -> bool:
    """
    Checks if all elements in a list are booleans.

    Args:
        - `list` (list): The list to check

    Returns:
        - `bool`: True if all elements are booleans, False otherwise
    """
    if not isinstance(args, list):
        raise TypeError(f"`list` argument must be a list. Got type {type(args)}")

    return all(isinstance(arg, bool) for arg in args)


def is_dict_str_str(dictionary: dict) -> bool:
    """
    Checks if all keys and values in a dictionary are strings.

    Args:
        - `dict` (dict): The dict to check

    Returns:
        - `bool`: True if all keys and values are strings, False otherwise
    """

    return (
        isinstance(dictionary, dict)
        and all(isinstance(arg, str) for arg in dictionary.keys())
        and all(isinstance(arg, str) for arg in dictionary.values())
    )


def is_dict_str_primitive_type(dictionary: dict) -> bool:
    """
    Checks if all keys and values in a dictionary are primitive types.

    Args:
        - `dict` (dict): The dict to check

    Returns:
        - `bool`: True if all keys and values are primitive types, False otherwise
    """

    return (
        isinstance(dictionary, dict)
        and all(isinstance(arg, str) for arg in dictionary.keys())
        and all(isinstance(arg, PrimitiveType) for arg in dictionary.values())
    )
