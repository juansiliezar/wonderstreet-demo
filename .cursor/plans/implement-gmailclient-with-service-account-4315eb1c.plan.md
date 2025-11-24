<!-- 4315eb1c-9673-460a-934e-9b02246627df 6311bc4a-cd82-44d1-aa03-d15f9cbbb466 -->
# Implement GmailClient with Service Account Authentication

## Overview

Implement `GmailClient` class in `integrations/gmail.py` using Google service account authentication with domain-wide delegation. Credentials will be loaded from `GMAIL_SERVICE_ACCOUNT_JSON` environment variable containing the full service account JSON as a string.

## Implementation Details

### Dependencies

Add to `pyproject.toml`:

- `google-auth>=2.23.0` - For service account credential management
- `google-auth-httpx>=0.2.0` (optional) - For httpx transport, OR manually add Authorization headers

### GmailClient Class Structure

**Location**: `integrations/gmail.py`

**Class Design**:

- Standalone class (no BaseAPIClient inheritance)
- Constructor accepts optional service account JSON string (from config/env)
- Uses `google-auth` to create service account credentials
- Uses `httpx.AsyncClient` for HTTP requests (consistent with codebase pattern)
- Implements domain-wide delegation via `credentials.with_subject(user_email)`

**Key Methods**:

1. `__init__(service_account_json: Optional[str] = None)`

   - Load service account JSON from parameter or `GMAIL_SERVICE_ACCOUNT_JSON` env var
   - Parse JSON and create `google.oauth2.service_account.Credentials`
   - Initialize `httpx.AsyncClient` with base Gmail API URL
   - Store base credentials (without subject) for later delegation

2. `ensure_token(user_to_impersonate: str) -> str`

   - Create delegated credentials using `credentials.with_subject(user_to_impersonate)`
   - Refresh token if needed using `delegated_credentials.refresh(Request())`
   - Return access token string
   - Cache token per user to avoid unnecessary refreshes

3. `_request(method: str, endpoint: str, user_to_impersonate: str, **kwargs) -> dict`

   - Get access token via `ensure_token(user_to_impersonate)`
   - Add `Authorization: Bearer {token}` header
   - Make async HTTP request using `httpx.AsyncClient`
   - Handle errors and retries (similar to BaseAPIClient pattern)
   - Return JSON response

4. `list_history(user_id: str, start_history_id: int) -> dict`

   - Calls `GET /gmail/v1/users/{user_id}/history?startHistoryId={start_history_id}`
   - Uses `_request()` with `user_id` as impersonation target
   - Returns history response dict

5. `get_message(user_id: str, message_id: str) -> dict`

   - Calls `GET /gmail/v1/users/{user_id}/messages/{message_id}`
   - Uses `_request()` with `user_id` as impersonation target
   - Returns message response dict

6. `close() -> None`

   - Closes `httpx.AsyncClient` connection
   - Async context manager support (`async with`)

### Configuration Updates

**Update `core/config.py` (when created in step 2)**:

- Add `GMAIL_SERVICE_ACCOUNT_JSON: Optional[str]` field
- Load from environment variable `GMAIL_SERVICE_ACCOUNT_JSON`
- Add `GMAIL_SCOPE` field (default: `"https://www.googleapis.com/auth/gmail.readonly"`)

### Code Structure

```python
# integrations/gmail.py structure
import json
import os
from typing import Optional, Dict
import httpx
from google.oauth2 import service_account
from google.auth.transport.requests import Request

class GmailClient:
    def __init__(self, service_account_json: Optional[str] = None):
        # Load and parse service account JSON
        # Create base credentials
        # Initialize httpx.AsyncClient
        
    async def ensure_token(self, user_to_impersonate: str) -> str:
        # Create delegated credentials
        # Refresh token
        # Return access token
        
    async def _request(self, method: str, endpoint: str, 
                      user_to_impersonate: str, **kwargs) -> dict:
        # Get token, make request, return JSON
        
    async def list_history(self, user_id: str, start_history_id: int) -> dict:
        # Call Gmail history API
        
    async def get_message(self, user_id: str, message_id: str) -> dict:
        # Call Gmail messages API
        
    async def close(self):
        # Close httpx client
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
```

### Error Handling

- Handle `ValueError` if service account JSON is missing or invalid
- Handle `google.auth.exceptions.RefreshError` for token refresh failures
- Handle `httpx.HTTPStatusError` for API errors
- Implement retry logic for 5xx errors (similar to BaseAPIClient)

### Keep Existing Function

- Preserve `decode_pubsub_message()` function as-is

## File Changes

**Modified files**:

- `pyproject.toml` - Add `google-auth>=2.23.0` dependency
- `integrations/gmail.py` - Add `GmailClient` class implementation
- `core/config.py` (future) - Add `GMAIL_SERVICE_ACCOUNT_JSON` and `GMAIL_SCOPE` fields

## Key Design Decisions

1. **Service Account JSON from Env**: Credentials loaded from `GMAIL_SERVICE_ACCOUNT_JSON` environment variable containing full JSON string
2. **Domain-Wide Delegation**: Uses `credentials.with_subject(user_email)` to impersonate users
3. **httpx for HTTP**: Uses `httpx.AsyncClient` (consistent with codebase) rather than googleapiclient
4. **Token Caching**: Cache tokens per user to minimize refresh calls
5. **Async Context Manager**: Supports `async with GmailClient() as client:` pattern

## Testing Considerations

- Mock `google.oauth2.service_account.Credentials` in unit tests
- Mock `httpx.AsyncClient` responses for API calls
- Test token refresh logic
- Test error handling for invalid credentials
- Test domain-wide delegation with different user emails

### To-dos

- [ ] Add google-auth>=2.23.0 to pyproject.toml dependencies
- [ ] Create GmailClient class in integrations/gmail.py with __init__ method that loads service account JSON from env var
- [ ] Implement ensure_token() method with domain-wide delegation using with_subject()
- [ ] Implement _request() method that adds Authorization header and makes httpx requests
- [ ] Implement list_history() and get_message() methods calling Gmail API endpoints
- [ ] Implement close() method and async context manager support
- [ ] Add error handling for credential loading, token refresh, and HTTP errors