import httpx
import os
import asyncio
import time
from typing import Optional, Dict, Any
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from dotenv import load_dotenv
from core.logging import logger

load_dotenv()


class GmailClient:
    # --- Class constants ---
    BASE_URL = "https://www.googleapis.com/gmail/v1"
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self, sa_json_path: Optional[str] = None):

        # Load service account JSON file
        sa_json_path = sa_json_path or os.getenv("GMAIL_SERVICE_ACCOUNT_FILE")
        if not sa_json_path:
            raise ValueError(
                "Service account JSON file not found."
                "Provide via parameter or GMAIL_SERVICE_ACCOUNT_FILE env var"
            )

        # Create base credentials
        self.base_credentials = service_account.Credentials.from_service_account_file(
            sa_json_path, scopes=self.SCOPES
        )

        # Initialize httpx.AsyncClient
        self.client = httpx.AsyncClient(base_url=self.BASE_URL, timeout=30.0)

        # Initialize token cache directory
        # This will store: user_email -> { "token": "...", "expires_at": 123456.78 }
        self.__token_cache: Dict[str, Dict[str, Any]] = {}

    async def ensure_token(self, user_to_impersonate: str) -> str:
        """
        Gets a valid, non-expired access token for a user
        - Checks if there is a valid token in the cache.
        - If not found or expired, refreshes the token in a separate thread.
        - Caches the new token and its expiration time

        Args:
            user_to_impersonate (str): _description_

        Returns:
            str: _description_
        """
        # --- 1. Check the cache for an existing token ---
        cached_token_info = self.__token_cache.get(user_to_impersonate)

        # Get the current timestamp
        # Add 60 second buffer to avoid network race conditions
        now = time.time() + 60

        if cached_token_info and cached_token_info["expires_at"] > now:
            # --- 2. CACHE HIT: Token found and not expired ---
            return cached_token_info["token"]

        # --- 3. CACHE MISS or Expired Token ---
        # If we're here, we need a new token, and to update the cache

        # Create a delegated credentials object
        delegated_creds = self.base_credentials.with_subject(user_to_impersonate)

        # Refresh Token Asynchronously
        logger.debug(f"Refreshing token for {user_to_impersonate}")
        try:
            await asyncio.to_thread(delegated_creds.refresh, Request())
        except Exception as e:
            # Handle case where DwD isn't set-up properly, user doesn't exist, etc
            logger.error(f"Error refreshing token for {user_to_impersonate}: {e}")
            raise ValueError(f"Failed to refresh token: {e}")

        # --- 4. Cache new token ---
        # delegated_creds.expiry is a datetime object which
        # needs to converted to a standard UNIX timestamp
        new_token_info = {
            "token": delegated_creds.token,
            "expires_at": delegated_creds.expiry.timestamp(),
        }

        self.__token_cache[user_to_impersonate] = new_token_info

        return new_token_info["token"]

    async def _request(
        self, method: str, endpoint: str, user_to_impersonate: str, **kwargs
    ) -> dict[str, Any]:
        """
        A private helper method to manke any authenticated API request.

        - Gets a valid token
        - Adds the `Authorization: Bearer {token} header to the request.
        - Makes the request using the httpx client.
        - Raises an error for bad responses (4xx, 5xx).
        - Returns the JSON response.
        """
        # 1. Get the token (handles caching, resfreshing)
        token = await self.ensure_token(user_to_impersonate)

        # 2. Add the token the headers
        # We .pop() `headers` from kwargs in case the caller provides their own
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"

        # 3. Make the request
        try:
            response = await self.client.request(
                method=method,
                url=endpoint,
                headers=headers,
                **kwargs,  # passes along any other params, like `json` or `params`
            )

            # 4. Check for errors
            response.raise_for_status()

            # 5. Return the JSON response
            return response.json()

        except httpx.HTTPStatusError as e:
            # Re-raise with a more informative error message
            logger.error(f"HTTP Error for {user_to_impersonate}: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error during request: {e}")
            raise e

    async def list_history(
        self, user_id: str, start_history_id: int, user_to_impersonate: str
    ) -> Dict[str, Any]:
        """
        Fetches all history records for a user since a given history ID.

        Args:
            user_id: The user's email address, or "me".
            start_history_id: The ID to start the history search from.
            user_to_impersonate: The email address of the user to act as.

        Returns:
            A dictionary containing the list of history records.
        """
        return await self._request(
            method="GET",
            endpoint=f"/users/{user_id}/history",
            user_to_impersonate=user_to_impersonate,
            params={
                "startHistoryId": str(start_history_id),
                "historyTypes": "messageAdded",  # only gets new messages
            },
        )

    async def get_message(
        self, user_id: str, message_id: str, user_to_impersonate: str
    ) -> Dict[str, Any]:
        """
        Gets a single, full email message object.

        Args:
            user_id: The user's email address, or "me".
            message_id: The ID of the message to fetch.
            user_to_impersonate: The email address of the user to act as.

        Returns:
            A dictionary containing the full message resource.
        """
        return await self._request(
            method="GET",
            endpoint=f"/users/{user_id}/messages/{message_id}",
            user_to_impersonate=user_to_impersonate,
            params={"format": "full"},  # Request the full email payload
        )

    # --- Cleanup and context management ---

    async def close(self):
        """
        Saves and closes the underlying httpx client.
        """
        logger.debug("Closing httpx client...")
        await self.client.aclose()
        self.__token_cache.clear()  # Clear the token cache

    async def __aenter__(self):
        """
        Allows the client to be used as an async context manager.
        Usage: `async with GmailClient() as client:`
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Cleans up the client when the `async with` block is exited.
        """
        await self.close()
