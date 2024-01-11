import pytest
import vertix.tests.helpers.helper_functions as helper


def test_try_except_block_handler() -> None:
    """Test that try_except_block_handler works as expected"""
    helper.try_except_block_handler(
        lambda: None,
        Exception,
        "Exception was raised when it should not have been",
    )
    with pytest.raises(pytest.fail.Exception):
        helper.try_except_block_handler(
            lambda: 1 / 0,
            Exception,
            "Exception was not raised when it should have been",
        )
