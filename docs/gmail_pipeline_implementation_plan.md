# Next Steps: Complete Gmail Integration & Email Processing Pipeline

## Current State Summary

**Completed:**

- Project structure and architecture documentation
- Email domain models (PubSubMessageData, PubSubMessage, PubSubPushRequest)
- Gmail webhook endpoint (`/webhooks/gmail`) that receives Pub/Sub notifications
- GmailClient class skeleton with method stubs
- Gmail watch setup script (`watch.py`)
- Core logging infrastructure
- Property management domain models

**Incomplete:**

- `GmailClient` implementation (all methods are stubs)
- Email ingestion pipeline (`domains/email/ingestion.py` is empty)
- Email parsing (`domains/email/parsing.py` is empty)
- Email classification (`domains/email/classification.py` is empty)
- FastAPI app initialization in `main.py` (currently placeholder)
- Router registration and app setup

## Implementation Plan

### Phase 1: Complete GmailClient Implementation

**File: `integrations/gmail.py`**

Implement the following methods:

1. `__init__`: Load service account JSON from file path or environment variable
2. `ensure_token`: Create delegated credentials with domain-wide delegation, refresh token, return access token
3. `_request`: Generic HTTP request method using httpx with OAuth token
4. `list_history`: Call Gmail API `users().history().list()` to get changes since a history ID
5. `get_message`: Call Gmail API `users().messages().get()` to fetch full message details
6. `close`: Properly close httpx client

**Key Requirements:**

- Use service account JSON file (path from env or parameter)
- Support domain-wide delegation (impersonate users)
- Use httpx.AsyncClient for async HTTP requests
- Handle token refresh automatically
- Return parsed JSON responses

### Phase 2: Implement Email Ingestion Pipeline

**File: `domains/email/ingestion.py`**

Create functions to:

1. `process_gmail_webhook`: Main entry point that takes PubSubPushRequest

- Decode and validate the Pub/Sub message
- Use GmailClient to fetch email changes since last history ID
- For each new message, fetch full email details
- Call parsing and classification functions
- Return processed results

2. `fetch_email_changes`: Helper to get history changes from Gmail API
3. `fetch_email_details`: Helper to get full message payload

**Integration Points:**

- Import `GmailClient` from `integrations.gmail`
- Import models from `domains.email.models`
- Call parsing and classification modules (to be implemented in Phase 3)

### Phase 3: Implement Email Parsing

**File: `domains/email/parsing.py`**

Create functions to extract structured data from Gmail message objects:

1. `parse_gmail_message`: Main parser that takes Gmail API message dict

- Extract sender, recipients, subject, body
- Parse headers (Date, Message-ID, Thread-ID, etc.)
- Handle multipart MIME structure
- Extract attachments metadata
- Return structured Pydantic model

2. Create Pydantic models for parsed email:

- `ParsedEmail`: Main model with all extracted fields
- `EmailHeader`: Model for email headers
- `EmailAttachment`: Model for attachment metadata

### Phase 4: Implement Email Classification

**File: `domains/email/classification.py`**

Create classification logic:

1. `classify_email`: Main classifier that takes ParsedEmail

- Rule-based classification (can be enhanced with ML later)
- Categories: lead, client, spam, internal, maintenance_request, etc.
- Extract entities (property addresses, tenant names, etc.)
- Return classification result with confidence score

2. Create Pydantic models:

- `EmailClassification`: Model with category, confidence, entities

### Phase 5: Wire Everything Together

**File: `main.py`**

1. Initialize FastAPI app
2. Set up logging using `core.logging.setup_logging()`
3. Register email router: `app.include_router(email_router, prefix="/api/v1")`
4. Add health check endpoint
5. Configure CORS if needed
6. Add startup/shutdown event handlers

**File: `api/v1/routers/email.py`**

1. Replace placeholder code with actual ingestion call
2. Import and use `process_gmail_webhook` from `domains.email.ingestion`
3. Add proper error handling and logging
4. Store history ID for future webhook calls (in-memory for now, database later)

### Phase 6: Testing & Validation

1. Test GmailClient with real service account
2. Test webhook endpoint with sample Pub/Sub payload
3. Verify email parsing extracts correct data
4. Verify classification logic works
5. End-to-end test: Pub/Sub → Webhook → Gmail API → Parse → Classify

## Dependencies & Configuration

**Environment Variables Needed:**

- `GMAIL_SERVICE_ACCOUNT_FILE`: Path to service account JSON
- `GMAIL_USER_TO_IMPERSONATE`: Default user for domain-wide delegation (optional)

**Service Account Setup:**

- Must have domain-wide delegation enabled
- Must have Gmail API scope: `https://www.googleapis.com/auth/gmail.readonly`
- Pub/Sub topic must be configured in GCP

## Future Enhancements (Post-MVP)

- Store processed emails in database
- Store history IDs per email address for incremental sync
- Add retry logic for failed API calls
- Add rate limiting handling
- Implement email-to-CRM linking
- Add ML-based classification
- Add webhook signature verification for security