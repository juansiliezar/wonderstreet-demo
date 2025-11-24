<!-- 6838f572-419d-4ffe-8347-e4217f59da6f d14dc89d-6ad9-4654-8520-791e5e83f2d9 -->
# Refactor Gmail Webhook to Modular Architecture

## Overview

Transform the flat `api/v1/routers/email.py` implementation into a modular architecture that separates concerns across integration, domain, and API layers.

## Implementation Steps

### 1. Add FastAPI dependency (now)

- Update `pyproject.toml` to include `fastapi>=0.115.0` and `uvicorn[standard]>=0.32.0` in dependencies

### 2. Create core configuration module (later)

- Create `core/config.py` with Pydantic Settings for environment variable management
- Define `GmailSettings` class with:
- `GMAIL_CLIENT_ID` (from env)
- `GMAIL_CLIENT_SECRET` (from env)
- `GMAIL_TOKEN_ENDPOINT` (default: "https://oauth2.googleapis.com/token")
- `GMAIL_SCOPE` (default: "https://www.googleapis.com/auth/gmail.readonly")
- Use `python-dotenv` to load `.env` file

### 3. Implement core logging (now)

- Update `core/logging.py` with:
- `setup_logging()` function that configures Python logging
- Module-level logger instance
- Format: `[%(asctime)s] %(levelname)s - %(name)s - %(message)s`
- Use `logging.INFO` as default level

### 4. Implement GmailClient in integrations/gmail.py (now)

- Add `GmailClient` class (standalone, no BaseAPIClient inheritance)
- Constructor accepts optional OAuth2 credentials (from config)
- Implement `ensure_token(user_to_impersonate: str)` for domain-wide delegation
- Implement `_request()` method with token management
- Implement `list_history(user_id: str, start_history_id: int)` method
- Implement `get_message(user_id: str, message_id: str)` method
- Implement `close()` method for cleanup
- Keep existing `decode_pubsub_message()` function

### 5. Implement email ingestion service (now)

- Update `domains/email/ingestion.py` with:
- `process_notification(gmail_data: PubSubMessageData)` async function
- Import and use `GmailClient` from integrations
- Use `core.logging.logger` instead of print statements
- Fetch history changes and messages
- Add TODO comments for parsing and database persistence

### 6. Refactor email router (now)

- Update `api/v1/routers/email.py`:
- Remove FastAPI app instantiation (move to main.py)
- Create `APIRouter` with prefix `/webhooks/gmail` and tag `["Email - Pub/Sub"]`
- Import models from `domains.email.models`
- Import `decode_pubsub_message` from `integrations.gmail`
- Import `process_notification` from `domains.email.ingestion`
- Implement `handle_gmail_webhook()` endpoint:
- Accept `PubSubPushRequest`
- Decode message using `decode_pubsub_message()`
- Use `BackgroundTasks` to call `process_notification()` asynchronously
- Return `{"status": "accepted"}` on success
- Handle exceptions with appropriate HTTP status codes

### 7. Update main.py (now)

- Replace placeholder with FastAPI application setup:
- Import FastAPI
- Import email router
- Call `core.logging.setup_logging()`
- Create FastAPI app instance
- Include email router
- Add root endpoint for health check (optional)

## File Changes Summary

**New files:**

- `core/config.py` - Configuration management with Pydantic Settings

**Modified files:**

- `pyproject.toml` - Add FastAPI and uvicorn dependencies
- `core/logging.py` - Implement logging setup
- `integrations/gmail.py` - Add GmailClient class (keep existing decode function)
- `domains/email/ingestion.py` - Implement process_notification function
- `api/v1/routers/email.py` - Refactor to use router pattern
- `main.py` - Set up FastAPI application

## Key Design Decisions

1. **No BaseAPIClient**: GmailClient is standalone to avoid coupling
2. **Domain-wide delegation**: OAuth2 token includes `subject` parameter for impersonation
3. **Background tasks**: Email processing happens asynchronously to avoid blocking webhook response
4. **Configuration**: Use Pydantic Settings for type-safe env var loading
5. **Logging**: Standard Python logging instead of print statements

## Testing Considerations

- Router can be tested independently with FastAPI TestClient
- GmailClient can be mocked for unit tests
- Ingestion service can be tested with mock GmailClient
- Configuration can be overridden in tests via environment variables

### To-dos

- [x] Add FastAPI and uvicorn to pyproject.toml dependencies
- [ ] Create core/config.py with GmailSettings using Pydantic Settings
- [ ] Implement setup_logging() and logger in core/logging.py
- [ ] Add GmailClient class to integrations/gmail.py with OAuth2 and API methods
- [ ] Implement process_notification() function in domains/email/ingestion.py
- [ ] Refactor api/v1/routers/email.py to use APIRouter pattern with background tasks
- [ ] Update main.py to set up FastAPI app and register email router