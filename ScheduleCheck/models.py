from mongoengine import Document, StringField, DateTimeField, UUIDField, IntField

class ScheduledNotification(Document):
    """
    Representing a notification that will be sent in the future
    """

    MAX_SEND_ATTEMPTS = 3

    identifier = UUIDField(required=True)
    identifier_type = StringField(
        required=True, choices=["team_id", "user_id"])
    message_title = StringField(required=True)
    message_body = StringField(required=True)
    time = DateTimeField(required=True)
    notification_type = StringField(required=True, choices=[
                                    "new_comment_added", "new_activity_added", "activity_completed", "activity_start_reminder"])
    attempt = IntField(default=0)
    meta = {"indexes": ["time"], "auto_create_index": True}
