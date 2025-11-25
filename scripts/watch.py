import os
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()  # Load variables from .env file

# 1. Get the path to your key file from .env
SERVICE_ACCOUNT_FILE = os.getenv("GMAIL_SERVICE_ACCOUNT_FILE")

# 2. The email of the user you are impersonating
#    (The user you gave DwD access to in the Admin Console)
USER_TO_IMPERSONATE = "juan@wonder-st.com"

# 3. The email you want to watch
#    (Can be the same as above, or 'me', or another user)
EMAIL_TO_WATCH = "juan@wonder-st.com"

# 4. Your GCP Project ID
PROJECT_ID = "cs-poc-32wimpgeypysqggnauzlyib"

# 5. The name of your Pub/Sub Topic
TOPIC_NAME = "gmail-notifications"
# ------------------------

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def create_gmail_watch():
    """
    Creates a one-time watch subscription on a Gmail account.
    """
    print(f"Loading credentials from: {SERVICE_ACCOUNT_FILE}")
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    print(f"Impersonating user: {USER_TO_IMPERSONATE}")
    delegated_creds = creds.with_subject(USER_TO_IMPERSONATE)

    try:
        service = build("gmail", "v1", credentials=delegated_creds)

        # The request body for the watch call
        request_body = {
            "labelIds": ["INBOX"],
            "topicName": f"projects/{PROJECT_ID}/topics/{TOPIC_NAME}",
        }

        print(f"Attempting to watch mailbox: {EMAIL_TO_WATCH}...")
        print(f"Notifying Pub/Sub topic: {request_body['topicName']}")

        # Make the API call
        response = (
            service.users().watch(userId=EMAIL_TO_WATCH, body=request_body).execute()
        )

        print("\n✅ Success! Watch call successful.")
        print(f"  History ID: {response['historyId']}")
        print(f"  Expiration: {response['expiration']}")
        print("\nYour endpoint will now start receiving notifications.")

    except HttpError as error:
        print(f"\n❌ An error occurred: {error}")
        print("\n--- Common Issues ---")
        print(
            "1. 403: Make sure Domain-Wide Delegation is enabled and scopes are authorized in admin.google.com."
        )
        print("2. 403: Make sure the Gmail API is enabled in your GCP project.")
        print("3. 404: Make sure the Topic Name and Project ID are correct.")
        print(
            "4. 400: Make sure the 'gmail-api-push@system.gserviceaccount.com' has 'Pub/Sub Publisher' role on your topic."
        )


if __name__ == "__main__":
    if not all(
        [
            SERVICE_ACCOUNT_FILE,
            USER_TO_IMPERSONATE,
            EMAIL_TO_WATCH,
            PROJECT_ID,
            TOPIC_NAME,
        ]
    ):
        print(
            "Error: Missing configuration. Please update the variables at the top of the script."
        )
    else:
        create_gmail_watch()
