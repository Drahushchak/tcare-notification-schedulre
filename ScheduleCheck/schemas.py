import datetime
from uuid import uuid4
from bson import ObjectId
from pydantic import BaseModel, Field
from pydantic.types import UUID4
from typing_extensions import Literal

class PydanticObjectId(str):
    """
    Validate if a given string can be considered a valid ObjectId
    """
    EXAMPLE = "507f191e810c19729de860ea"

    def __new__(cls, value):
        # perform pre validation logic here
        # Convert the vlue to a string
        value = str(value)

        # Now call the superclass(str) __new__ method with the pre-processed value
        return super().__new__(cls, value)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return str(v)

Identifier = UUID4
IdentifierType = Literal["team_id", "user_id"]
NotificationType = Literal["new_comment_added", "new_activity_added", "activity_completed", "activity_start_reminder"]
BulkNotificationStatus = Literal["success", "receiver_not_found", "not_sent", "error"]

class ModifiedBaseModel(BaseModel):

    class Config:
        arbitrary_types_allowed=True

class NotificationBase(ModifiedBaseModel):
    message_title: str
    message_body: str
    notification_type: NotificationType


class Notification(NotificationBase):
    identifier: Identifier = Field(..., examples=[uuid4()])
    identifier_type: IdentifierType


class NotificationWithId(Notification):
    id: PydanticObjectId = Field(..., examples=[str(ObjectId())])

class ScheduledNotificationBaseSchema(ModifiedBaseModel):
    identifier: Identifier = Field(..., examples=[uuid4()])
    identifier_type: IdentifierType
    message_title: str
    message_body: str
    time: datetime.datetime
    notification_type: NotificationType
