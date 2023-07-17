from ScheduleCheck.config import settings
from mongoengine import connect, disconnect


# Connect to the MongoDB database using the separate connection properties
def connect_to_mongo():
    connect(
        db=settings.mongodb_database,
        host=settings.mongodb_host,
        port=settings.mongodb_port,
        username=settings.mongodb_username,
        password=settings.mongodb_password,
        ssl=settings.mongodb_ssl,
        retrywrites=settings.mongodb_retrywrites,
    )


def disconnect_from_mongo():
    disconnect()
