from fastapi import APIRouter, Request, HTTPException, status
from domains.email.models import PubSubPushRequest
from domains.email.ingestion import process_gmail_webhook
from integrations.gmail import GmailClient
from core.logging import logger


router = APIRouter()


@router.post("/webhooks/gmail")
async def handle_gmail_webhook(request: PubSubPushRequest):
    """
    Receives push notifications from Google Cloud Pub/Sub
    """
    try:
        # Creates a new GmailClient per request for simplicity during testing.
        # This approach is inefficient and will be optimized in main.py.
        logger.info("Gmail webhook received, starting ingestion...")

        async with GmailClient() as client:
            processed_emails = await process_gmail_webhook(request, client)

        logger.info(f"Successfully processed {len(processed_emails)} emails.")

        # Returns 204 No Content to acknowledge successful receipt to Pub/Sub.
        return "", status.HTTP_204_NO_CONTENT

    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        # Returns 500 to signal Pub/Sub to retry the webhook delivery.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )
