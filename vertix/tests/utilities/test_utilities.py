import pytest

import vertix.utilities.utilities as utils


# Tests for all_are_strings
@pytest.mark.parametrize(
    "input_list, expected",
    [
        (["a", "b", "c"], True),
        (["a", 1, "c"], False),
        ([], True),
        ([True], False),
        ([""], True),
        ([{}], False),
        ([()], False),
    ],
)
def test_all_are_strings(input_list: list, expected: bool) -> None:
    assert utils.all_are_strings(input_list) == expected


# Tests error handling in all_are_strings
@pytest.mark.parametrize(
    "input_list",
    [
        ("not a list"),
        (123),
        (True),
        ({}),
        ((1, 2, 3)),
    ],
)
def test_all_are_strings_error_handling(input_list: list) -> None:
    with pytest.raises(TypeError):
        utils.all_are_strings(input_list)


# Tests for all_are_bool
@pytest.mark.parametrize(
    "input_list, expected",
    [([True, False, True], True), ([True, "False", 1], False), ([], True)],
)
def test_all_are_bool(input_list: list, expected: bool) -> None:
    assert utils.all_are_bool(input_list) == expected


# Tests error handling in all_are_bool
@pytest.mark.parametrize(
    "input_list",
    [("not a list"), (123), (True), ({}), ((1, 2)), (1.2)],
)
def test_all_are_bool_error_handling(input_list: list) -> None:
    with pytest.raises(TypeError):
        utils.all_are_bool(input_list)


# Tests for is_dict_str_str
@pytest.mark.parametrize(
    "input_dict, expected",
    [
        ({"a": "1", "b": "2"}, True),
        ({1: "a", 2: "b"}, False),
        ({"a": 1, "b": 2}, False),
        ({}, True),
        (["not", "a", "dict"], False),
        ("not a dict", False),
        ((), False),
        ({"a": {}}, False),
        ({"a": ()}, False),
        ({"a": []}, False),
        ({"a": ["a", "b"]}, False),
        ({"a": {"a": "b"}}, False),
        ({"a": {"a": "b"}, "c": "d"}, False),
    ],
)
def test_is_dict_str_str(input_dict: dict, expected: bool) -> None:
    assert utils.is_dict_str_str(input_dict) == expected
