from typing import Callable, Type

import pytest


def try_except_block_handler(
    executable: Callable, error_type: Type[Exception], error_msg: str
) -> None:
    """Try/except block handler for testing"""
    try:
        executable()
    except error_type:
        pytest.fail(error_msg)


def set_attributes(model: object, attributes: dict) -> None:
    """Set attributes on a model"""
    for key, value in attributes.items():
        setattr(model, key, value)
