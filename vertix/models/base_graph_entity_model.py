from datetime import datetime
import logging
from typing import Generic, Literal, TypeVar
import uuid

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)
from pydantic.fields import FieldInfo

from vertix.typings import (
    AttributeDictType,
    PrimitiveType,
)


T = TypeVar("T", bound="BaseGraphEntityModel")


class BaseGraphEntityModel(BaseModel, Generic[T], validate_assignment=True):
    """
    DO NOT USE THIS CLASS DIRECTLY. INHERIT FROM IT INSTEAD.
        - Note: The ability to inherit from this class is not yet implemented, but is on the roadmap.

    A base class for models to be used in the ORM for the graph databases.

    Attributes:
        - `id` (str): The primary key for the the model, used to create edges (defaults to a `uuid4`)
        - `vrtx_model_type` (str): The model type. If using Vertix standard models, this will be `'node'` or `'edge'` defined in the
            Node and Edge models respectively. (defaults to an empty string)
        - `table` (str): The table name (defaults to an empty string)
        - `label` (str): A custom label for the node (defaults to an empty string)
        - `document` (str): A string used for vector embedding and similarity search or as other information in the graph (defaults to an empty string)
        - `created_at` (str): The time at creation (defaults to the current time)
        - `updated_at` (str): The time at the last update (defaults to the current time)
        - `additional_attributes` (AttributeDictType): Any additional attributes assigned to the model using the `additional_attributes` field
            - `AttributeDictType` is defined in `vertix/typings/__init__.py` as:
                - `dict[str, str | int | float | bool]`


    Methods:
        - `serialize()`: Serializes the node into a flattened dictionary with only primitive types.
        - `deserialize(data)`: Class method that deserializes a dictionary into a model instance.
    """

    id: str = Field(
        description="The primary key.",
        default_factory=lambda: str(uuid.uuid4()),
    )
    vrtx_model_type: str = Field(
        description="The model type. If using Vertix standard models, this will be 'node' or 'edge'.",
        default="",
    )
    table: str = Field(
        description="The table name.",
        default="",
    )
    document: str = Field(
        description="A string used for vector embedding and similarity search or as other information in the graph.",
        default="",
    )
    created_at: str = Field(
        description="The time at creation, only to be set when coming from the database",
        default="",
    )
    updated_at: str = Field(
        description="The time at the last update, only to be set when coming from the database",
        default="",
    )
    additional_attributes: AttributeDictType = Field(
        description="A dictionary of additional attributes. Values must be primitive types.",
        default_factory=dict,
    )

    @staticmethod
    def _current_time() -> str:
        """Returns the current timestamp in isoformat"""
        return datetime.utcnow().isoformat()

    @field_validator("additional_attributes", mode="before")
    def _validate_additional_attributes(cls, v: AttributeDictType) -> AttributeDictType:
        """
        Validates the `additional_attributes` field ensuring that it conforms to the
        `AttributeDictType` type.

        `AttributeDictType` is defined in `vertix/typings/__init__.py` as:
            - `dict[str, str | int | float | bool]`

        Raises:
            - `TypeError`: If `additional_attributes` is not a dictionary
            - `TypeError`: If `additional_attributes` keys are not strings
            - `TypeError`: If `additional_attributes` values are not strings, ints, floats, or booleans
        """
        if not isinstance(v, dict):
            raise TypeError("`additional_attributes` must be a dictionary")
        for key, value in v.items():
            if not isinstance(key, str):
                raise TypeError("`additional_attributes` keys must be strings")
            if not isinstance(value, (str, int, float, bool)):
                raise TypeError(
                    "`additional_attributes` values must be strings, ints, floats, or booleans"
                )
        return v

    @field_validator("created_at", mode="before")
    def _validate_created_at(cls, value: str) -> str:
        """
        Validates the `created_at` field.

        Raises:
            - `ValueError`: If `created_at` is after the current time, or if it is not a valid isoformat string
            - `TypeError`: If `created_at` is not a string
        """

        try:
            created_at: datetime = datetime.fromisoformat(value)
            current_time: datetime = datetime.fromisoformat(cls._current_time())

            if created_at > current_time:
                raise ValueError("`created_at` must be before the current time")
        except ValueError:
            raise ValueError("`created_at` must be a valid isoformat string")
        return value

    @field_validator("updated_at", mode="before")
    def _validate_updated_at(cls, value: str) -> str:
        """
        Validates the `updated_at` field.

        Raises:
            - `ValueError`: If `updated_at` is after the current time, or if it is not a valid isoformat string
            - `TypeError`: If `updated_at` is not a string
        """
        try:
            updated_at: datetime = datetime.fromisoformat(value)
            current_time: datetime = datetime.fromisoformat(cls._current_time())

            if updated_at > current_time:
                raise ValueError("`updated_at` must be before the current time")
        except ValueError:
            raise ValueError("`updated_at` must be a valid isoformat string")
        return value

    @model_validator(mode="before")
    def _validate_created_at_and_updated_at_together(
        cls, values: dict[str, PrimitiveType]
    ) -> dict[str, PrimitiveType]:
        """
        Validates that created_at and `updated_at` are provided together and the created_at is equal
        to or before the `updated_at`.

        Raises:
            - `ValueError`: If created_at is after `updated_at`, or if one is provided without the other
            - `TypeError`: If created_at or `updated_at` are not strings
        """
        created_at: PrimitiveType | None = values.get("created_at")
        updated_at: PrimitiveType | None = values.get("updated_at")

        if (created_at is not None and updated_at is None) or (
            created_at is None and updated_at is not None
        ):
            raise ValueError("`created_at` and `updated_at` must be provided together")

        if values.get("created_at") and values.get("updated_at"):
            if values["created_at"] > values["updated_at"]:  # type: ignore
                raise ValueError("`created_at` must be before `updated_at`")

        return values

    def serialize(self) -> dict[str, PrimitiveType]:
        """
        Serializes the node into a flattened dictionary with only primitive types.

        `PrimitiveType` is defined in `vertix/typings/__init__.py` as:
            - `str | int | float | bool`

        Returns:
            - `dict[str, PrimitiveType]`: A dictionary of the node's attributes

        Raises:
            - `Exception`: If the node cannot be serialized
        """

        current_time: str = self._current_time()
        if self.created_at == "":
            self.created_at = current_time
        self.updated_at = current_time
        return {
            **self.model_dump(exclude={"additional_attributes"}),
            **self.additional_attributes,
        }

    @classmethod
    def deserialize(cls: type[T], data: dict[str, PrimitiveType]) -> T:
        """
        Deserializes a dictionary into a model instance.

        This method will return an instance of the subclass that calls it. If called on a `Node`
        class, it will return a `Node` instance. If called on an `Edge` class, it will return an
        `Edge` instance.

        Args:
            - `data` (`dict[str, PrimitiveType]`): A dictionary of the model's expected attributes
                - `PrimitiveType` is defined in `vertix/typings/__init__.py` as:
                    - `str | int | float | bool`

        Returns:
            - `Node` | `Edge`: An instance of the model class that called the method with the
                attributes set to the values in `data`

        Raises:
            - `TypeError`: If the data is not a dictionary
        """
        if not isinstance(data, dict):
            raise TypeError("`data` argument must be a dictionary")

        declared_attrs = {}

        fields: dict[str, FieldInfo] = cls.model_fields
        for field_name in fields.keys():
            if field_name in data:
                value = data[field_name]
                declared_attrs[field_name] = value

        additional_attrs: dict[str, PrimitiveType] = {
            key: value for key, value in data.items() if key not in fields
        }

        instance: T = cls(**declared_attrs)
        instance.additional_attributes = additional_attrs

        return instance
