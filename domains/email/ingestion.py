import base64
import json
from typing import Any, Dict, List

from domains.email.models import PubSubPushRequest, PubSubMessageData
from integrations.gmail import GmailClient
from core.logging import logger


def decode_pubsub_message(payload: PubSubPushRequest) -> PubSubMessageData:
    """Extracts and decodes base64-encoded Gmail Pub/Sub message data.

    Args:
        payload: The Pub/Sub push request containing encoded message data.

    Returns:
        Decoded Pub/Sub message data as a validated model instance.
    """
    raw_data = base64.b64decode(payload.message.data).decode("utf-8")
    data_json = json.loads(raw_data)
    return PubSubMessageData(**data_json)


async def process_gmail_webhook(
    payload: PubSubPushRequest, gmail_client: GmailClient
) -> List[Dict[str, Any]]:
    """
    Main ingestion pipeline entry point for processing Gmail webhooks.

    Processes incoming Pub/Sub notifications by decoding the message, fetching
    Gmail history changes, and retrieving full email details for each new
    message. Future enhancements will include parsing and classification.

    Args:
        payload: The Pub/Sub push request containing Gmail notification data.
        gmail_client: Authenticated Gmail client for API interactions.

    Returns:
        List of raw Gmail message dictionaries for each newly received email.
    """
    logger.info("---New Webhook Received---")

    # Decodes and validates the Pub/Sub message payload.
    gmail_data = decode_pubsub_message(payload)
    logger.info(f"Processing for: {gmail_data.email_address}")
    logger.info(f"History ID: {gmail_data.history_id}")
    processed_emails = []

    try:
        # Fetches Gmail history changes since the last processed history ID.
        history_response = await gmail_client.list_history(
            user_id="me",
            start_history_id=gmail_data.history_id,
            user_to_impersonate=gmail_data.email_address,
        )

        history_items = history_response.get("history", [])
        if not history_items:
            logger.info("No new history items found.")
            return []

        # Iterates through history items to fetch full details for each new message.
        for item in history_items:
            messages_added = item.get("messagesAdded", [])
            for msg_summary in messages_added:
                msg_id = msg_summary["message"]["id"]
                logger.info(f"Fetching new message ID: {msg_id}")

                # Fetches the complete email message using the Gmail API.
                email = await gmail_client.get_message(
                    user_id="me",
                    message_id=msg_id,
                    user_to_impersonate=gmail_data.email_address,
                )

                logger.info(f"  -> Fetched Subject: {get_subject(email)}")
                processed_emails.append(email)

                # TODO(phase-3): Parse email content and extract structured data.
                # parsed_email = parse_gmail_message(email)

                # TODO(phase-4): Classify email type and route to appropriate handler.
                # classification = classify_email(parsed_email)

    except Exception as e:
        logger.error(f"Error processing email ingestion: {e}", exc_info=True)
        # Re-raises exception to be handled by the API router layer.
        raise e

    logger.info(f"--- Successfully processed {len(processed_emails)} emails ---")
    return processed_emails


def get_subject(message: Dict[str, Any]) -> str:
    """Extracts the Subject header from a Gmail message.

    Args:
        message: Raw Gmail message dictionary from the API.

    Returns:
        The email subject line, or "[No Subject]" if not found.
    """
    headers = message.get("payload", {}).get("headers", [])
    for header in headers:
        if header["name"].lower() == "subject":
            return header["value"]
    return "[No Subject]"
