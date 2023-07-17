import datetime
import json
import logging
from typing import Iterable

import azure.functions as func
import requests

from ScheduleCheck.database import connect_to_mongo, disconnect_from_mongo
from ScheduleCheck.models import ScheduledNotification
from ScheduleCheck.schemas import NotificationWithId, PydanticObjectId, ScheduledNotificationBaseSchema
from ScheduleCheck.config import settings

def increment_attempt(notification: ScheduledNotification) -> None:
    """
    Function to increment the attempt count of a scheduled notification.
    If the notification has reached the maximum number of attempts, it is deleted.
    """
    if notification.attempt == notification.MAX_SEND_ATTEMPTS - 1:
        notification.delete()
        return
    notification.attempt += 1
    notification.save()

def get_schedule_request_data(scheduled_notifications: Iterable[ScheduledNotification]):
    """
    Formats the scheduled notifications data from the database to be sent as a POST request
    """
    return [
        NotificationWithId(
            id=PydanticObjectId(schedule.id),
            identifier=schedule.identifier,
            identifier_type=schedule.identifier_type,
            message_title=schedule.message_title,
            message_body=schedule.message_body,
            notification_type=schedule.notification_type,
        ).model_dump(mode="json")
        for schedule in scheduled_notifications
    ]


def main(mytimer: func.TimerRequest) -> None:
    connect_to_mongo()
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    scheduled_notifications = ScheduledNotification.objects(time__lte=utc_timestamp)  # type: ignore

    if not scheduled_notifications:
        logging.info("No scheduled notifications to send")
        return

    data = get_schedule_request_data(scheduled_notifications)

    logging.info("Sending %s notifications", len(data))

    response = requests.post(
        settings.base_url + '/notify/',
        data=json.dumps(data),
    )

    if response.status_code != 200:
        logging.error("Error sending notifications: %s", response.text)
        for notification in scheduled_notifications:
            logging.info("Incrementing attempt for notification %s", notification.id)
            increment_attempt(notification)
        return

    bulk_notification_status = response.json()

    for notification in scheduled_notifications:
        if bulk_notification_status[str(notification.id)] == "receiver_not_found":
            logging.info("Receiver not found for notification %s", notification.id)
            logging.info("Incrementing attempt for notification %s", notification.id)
            increment_attempt(notification)
        else:
            logging.info("Deleting notification %s from scheduled list", notification.id)
            notification.delete()

    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
    disconnect_from_mongo()
