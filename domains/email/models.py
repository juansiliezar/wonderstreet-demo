from pydantic import BaseModel, Field


class PubSubMessageData(BaseModel):
    """Decoded Gmail notification data from Pub/Sub message payload.

    Contains the email address and history ID that identify which Gmail
    account received new messages and the point in history to query from.
    """

    email_address: str = Field(..., alias="emailAddress")
    history_id: int = Field(..., alias="historyId")


class PubSubMessage(BaseModel):
    """Pub/Sub message envelope containing encoded notification data.

    Wraps the base64-encoded payload along with message metadata such as
    message ID and publish timestamp from Google Cloud Pub/Sub.
    """

    data: str
    message_id: str = Field(..., alias="messageId")
    publish_time: str = Field(..., alias="publishTime")


class PubSubPushRequest(BaseModel):
    """Complete Pub/Sub push notification request body.

    Represents the full webhook payload sent by Google Cloud Pub/Sub when
    Gmail push notifications are delivered to the configured subscription.
    """

    message: PubSubMessage
    subscription: str
