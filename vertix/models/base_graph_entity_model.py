from datetime import datetime
import uuid

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

from vertix.typings import (
    AttributeDictType,
    PrimitiveType,
)


class BaseGraphEntityModel(BaseModel, validate_assignment=True):
    """
    A base class for models to be used in the ORM for the graph databases.

    Attributes:
        - id (str): The primary key for the the model, used to create edges (defaults to a uuid4)
        - label (str): A custom label for the node (defaults to an empty string)
        - description (str): A description of the node (defaults to an empty string)
        - type (str): The type of node, used to create edges (defaults to "node")
        - neighbors_count (int): The number of neighbors this node has (defaults to 0)
        - created_at (str): The time at creation (defaults to the current time)
        - updated_at (str): The time at the last update (defaults to the current time)
        - Extras (PrimitiveType): Any additional attributes assigned to the model using the `additional_attributes` field


    Methods:
        - `serialize()`: Serializes the node into a flattened dictionary with only primitive types.
    """

    id: str = Field(
        description="The primary key.",
        default_factory=lambda: str(uuid.uuid4()),
    )
    label: str = Field(
        description="A custom label for the model.",
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
        Validates the additional attributes field

        Raises:
            - TypeError: If additional_attributes is not a dictionary
            - TypeError: If additional_attributes keys are not strings
            - TypeError: If additional_attributes values are not strings, ints, floats, or booleans
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
        Validates the created_at field.

        Raises:
            - ValueError: If created_at is after the current time, or if it is not a valid isoformat string
            - TypeError: If created_at is not a string
        """
        if not isinstance(value, str):
            raise TypeError("`created_at` must be a isoformat timestamp string")
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
        Validates the updated_at field.

        Raises:
            - ValueError: If updated_at is after the current time, or if it is not a valid isoformat string
            - TypeError: If updated_at is not a string
        """
        if not isinstance(value, str):
            raise TypeError("`updated_at` must be a isoformat timestamp string")
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
        Validates that created_at and updated_at are provided together and the created_at is equal
        to or before the updated_at.

        Raises:
            - ValueError: If created_at is after updated_at, or if one is provided without the other
            - TypeError: If created_at or updated_at are not strings
        """
        created_at: PrimitiveType | None = values.get("created_at")
        updated_at: PrimitiveType | None = values.get("updated_at")

        if (created_at is not None and updated_at is None) or (
            created_at is None and updated_at is not None
        ):
            raise ValueError("`created_at` and `updated_at` must be provided together")

        if values.get("created_at") and values.get("updated_at"):
            if not isinstance(values["created_at"], str) or not isinstance(
                values["updated_at"], str
            ):
                raise TypeError("`created_at` and `updated_at` must be strings")

            if values["created_at"] > values["updated_at"]:
                raise ValueError("`created_at` must be before `updated_at`")

        return values

    def serialize(self) -> dict[str, PrimitiveType]:
        """
        Serializes the node into a flattened dictionary with only primitive types.

        Returns:
            - dict[str, PrimitiveType]: A dictionary of the node's attributes

        Raises:
            - Exception: If the node cannot be serialized
        """

        try:
            current_time: str = self._current_time()
            if not self.created_at:
                self.created_at = current_time
            self.updated_at = current_time
            return {
                **self.model_dump(exclude={"additional_attributes"}),
                **self.additional_attributes,
            }

        except Exception as e:
            raise e
