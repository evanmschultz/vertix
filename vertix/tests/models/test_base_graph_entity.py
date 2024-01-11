from datetime import datetime, timedelta
from unittest.mock import patch

from pydantic import ValidationError
import pytest

from vertix.models.base_graph_entity_model import BaseGraphEntityModel
import vertix.tests.helper_functions as helper
from vertix.typings import PrimitiveType


@pytest.mark.parametrize(
    "id, label, document, should_raise",
    [
        ("test_id", "test_label", "test_document", False),
        (None, "test_label", "test_document", True),
        ("test_id", 123, "test_document", True),
        ("test_id", "test_label", (), True),
        ("test_id", "test_label", {}, True),
    ],
)
def test_base_graph_entity_model(
    id: str,
    label: str,
    document: str,
    should_raise: bool,
) -> None:
    """Test that BaseGraphEntityModel is validated correctly"""
    if should_raise:
        with pytest.raises(ValidationError):
            BaseGraphEntityModel(
                id=id,
                label=label,
                document=document,
            )
    else:
        helper.try_except_block_handler(
            lambda: BaseGraphEntityModel(
                id=id,
                label=label,
                document=document,
            ),
            ValidationError,
            "Unexpected ValidationError for BaseGraphEntity model instantiation",
        )


@pytest.mark.parametrize(
    "id, label, document, should_raise",
    [
        ("test_id", "test_label", "test_document", False),
        (None, "test_label", "test_document", True),
        ("test_id", 123, "test_document", True),
        ("test_id", "test_label", (), True),
    ],
)
def test_base_graph_entity_model_attribute_assignment_validation(
    id: str,
    label: str,
    document: str,
    should_raise: bool,
) -> None:
    """Test that attributes are validated correctly"""
    base_graph_entity = BaseGraphEntityModel()
    if should_raise:
        with pytest.raises(ValidationError):
            base_graph_entity.id = id
            base_graph_entity.label = label
            base_graph_entity.document = document
    else:
        helper.try_except_block_handler(
            lambda: helper.set_attributes(
                base_graph_entity, {"id": id, "label": label, "document": document}
            ),
            ValidationError,
            "Unexpected ValidationError for BaseGraphEntity model attribute assignment",
        )


@pytest.mark.parametrize(
    "created_at, updated_at, should_raise",
    [
        (1, None, True),  # Invalid type for created_at
        (None, "invalid", True),  # Invalid type for updated_at
        (
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat(),
            False,
        ),  # Valid timestamps
        (
            (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            datetime.utcnow().isoformat(),
            True,
        ),  # created_at later than updated_at
        (
            (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            True,
        ),  # Both timestamps in future
        (datetime.utcnow().isoformat(), "", True),  # missing updated_at
        ("", datetime.utcnow().isoformat(), True),  # missing created_at
    ],
)
def test_base_graph_entity_model_timestamp_validations(
    created_at: str, updated_at: str, should_raise: bool
) -> None:
    """Test that timestamps are validated correctly"""
    if should_raise:
        with pytest.raises(ValidationError):
            BaseGraphEntityModel(created_at=created_at, updated_at=updated_at)
    else:
        helper.try_except_block_handler(
            lambda: BaseGraphEntityModel(created_at=created_at, updated_at=updated_at),
            ValidationError,
            "Unexpected ValidationError for valid timestamps in BaseGraphEntity model",
        )


def test_base_graph_entity_timestamps_from_created_model() -> None:
    """Test updated_at timestamp is updated on serialization with existing data"""
    base_model = BaseGraphEntityModel(
        created_at="2021-01-01T00:00:00.000000", updated_at="2021-01-01T00:00:00.000000"
    )
    assert base_model.created_at == "2021-01-01T00:00:00.000000"
    assert base_model.created_at == base_model.updated_at

    base_model.serialize()
    assert base_model.created_at == "2021-01-01T00:00:00.000000"
    assert base_model.created_at < base_model.updated_at


@pytest.mark.parametrize(
    "additional_attributes, should_raise",
    [
        ({"key": "value"}, False),
        ({"key": 123}, False),
        ({"key": 1.2}, False),
        ({"key": True}, False),
        ([], True),
        ({1: "value"}, True),
        ({"key": [1, 2, 3]}, True),
        ({"key": {"key": "value"}}, True),
        ({"key": None}, True),
    ],
)
def test_base_graph_entity_model_additional_attributes_validation(
    additional_attributes: dict[str, PrimitiveType], should_raise: bool
) -> None:
    """Test that additional_attributes are validated correctly"""
    if should_raise:
        with pytest.raises(TypeError):
            BaseGraphEntityModel(additional_attributes=additional_attributes)
    else:
        assert BaseGraphEntityModel(additional_attributes=additional_attributes)


def test_base_graph_entity_model_serialization() -> None:
    """Test serialization of BaseGraphEntity model"""
    base_model = BaseGraphEntityModel(
        id="test_id",
        created_at="2021-01-01T00:00:00.000000",
        updated_at="2021-01-01T00:00:00.000000",
        label="test_label",
        document="test_document",
        additional_attributes={"test_attribute": True, "test_attribute2": 123},
    )
    expected_serialization = {
        "id": "test_id",
        "created_at": "2021-01-01T00:00:00.000000",
        "label": "test_label",
        "document": "test_document",
        "test_attribute": True,
        "test_attribute2": 123,
    }

    serialized_model: dict[str, PrimitiveType] = base_model.serialize()
    updated_at = serialized_model.pop("updated_at")
    assert isinstance(updated_at, str)
    assert updated_at > base_model.created_at
    assert serialized_model == expected_serialization


def test_base_graph_entity_model_serialization_exception_handling() -> None:
    """Test exception handling when serializing BaseGraphEntity model"""
    model = BaseGraphEntityModel()

    with patch.object(
        BaseGraphEntityModel, "model_dump", side_effect=Exception("Serialization Error")
    ):
        with pytest.raises(Exception) as excinfo:
            model.serialize()
        assert "Serialization Error" in str(excinfo.value)


@pytest.mark.parametrize(
    "id, label, document, additional_attributes, should_raise",
    [
        ("test_id", "test_label", "test_document", {"key": "example"}, False),
        (None, "test_label", "test_document", {}, True),
        ("test_id", 123, "test_document", {}, True),
        ("test_id", "test_label", (), {}, True),
        ("test_id", "test_label", {}, {}, True),
    ],
)
def test_base_graph_entity_model_deserialization(
    id: str,
    label: str,
    document: str,
    additional_attributes: dict[str, PrimitiveType],
    should_raise: bool,
) -> None:
    """Test deserialization of BaseGraphEntity model"""
    serialized_dict: dict[str, PrimitiveType] = {
        "id": id,
        "label": label,
        "document": document,
        **additional_attributes,
    }
    if should_raise:
        with pytest.raises(TypeError):
            BaseGraphEntityModel.deserialize(serialized_dict)
    else:
        helper.try_except_block_handler(
            lambda: BaseGraphEntityModel.deserialize(serialized_dict),
            ValidationError,
            "Unexpected ValidationError for BaseGraphEntity model deserialization",
        )
        deserialized: BaseGraphEntityModel = BaseGraphEntityModel.deserialize(
            serialized_dict
        )
        assert isinstance(deserialized, BaseGraphEntityModel)
        assert deserialized.id == id
        assert deserialized.label == label
        assert deserialized.document == document
        assert deserialized.additional_attributes == additional_attributes
