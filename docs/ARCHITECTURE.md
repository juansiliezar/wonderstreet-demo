# Wonder Street Demo: Architecture & Design Overview

## High-Level Architecture Pattern

This codebase follows a **vertical slice architecture** with three distinct integration-to-domain flows:

1. **Airtable ↔ Buildium Sync** (property management data synchronization)
2. **RLS Listing Integration** (MLS listings ingestion)
3. **Gmail Manager** (email automation and processing)

Each slice follows the pattern: **External Integration → Domain Logic → API Interface**

## Directory Structure & Organization

```
wonderstreet-demo/
├── api/v1/routers/          # FastAPI route handlers (presentation layer)
├── domains/                  # Business logic organized by domain
│   ├── email/               # Email processing domain
│   └── property_management/ # Property management domain
├── integrations/             # External API clients (infrastructure layer)
├── core/                     # Shared utilities and cross-cutting concerns
└── main.py                   # Application entry point
```

### Layer Responsibilities

- **`api/v1/routers/`**: HTTP endpoints, request/response handling, minimal business logic
- **`domains/`**: Business logic, domain models, orchestration between integrations
- **`integrations/`**: External API clients, authentication, data transformation
- **`core/`**: Logging, configuration, database, events (planned)

## Design Patterns & Principles

### 1. Domain-Driven Design (DDD)
- Domains are self-contained modules with their own models
- Business logic lives in domain modules, not in API routes
- Models use Pydantic for validation and type safety

### 2. Dependency Injection (Implicit)
- Integration clients are standalone classes
- Domain modules import from integrations (no explicit DI container)
- Python's module system provides natural dependency management

### 3. Data Validation
- Pydantic models throughout the codebase
- Type hints on all function signatures
- Models mirror external API schemas (e.g., Buildium OpenAPI)

### 4. Async/Await Pattern
- `GmailClient` uses async context managers (`__aenter__`, `__aexit__`)
- FastAPI endpoints are async
- HTTPX for async HTTP requests

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | FastAPI 0.121.2+ | REST API, async endpoints |
| **HTTP Client** | HTTPX 0.28.1+ | Async HTTP requests |
| **OAuth/Auth** | Authlib 1.6.5+, google-auth 2.43.0+ | OAuth2, service account auth |
| **Data Validation** | Pydantic 2 | Models, settings, validation |
| **Logging** | Loguru 0.7.3 | Structured logging |
| **Airtable** | PyAirtable 3.3.0+ | Airtable API client |
| **Package Manager** | uv (Astral) | Dependency management |
| **Python Version** | 3.11+ | Type hints, modern features |

## Current Implementation State

### ✅ Implemented
- Core logging (`core/logging.py`) with loguru
- Email domain models (`domains/email/models.py`) for Pub/Sub
- Gmail integration skeleton (`integrations/gmail.py`) with `GmailClient` class structure
- Email webhook router (`api/v1/routers/email.py`) with basic Pub/Sub handling
- Property management models (rentals, accounting, maintenance) from Buildium schema

### 🚧 In Progress / Planned
- `GmailClient` implementation (methods are stubs)
- Email ingestion pipeline (`domains/email/ingestion.py` is empty)
- Email parsing (`domains/email/parsing.py` is empty)
- Email classification (`domains/email/classification.py` is empty)
- Buildium integration (`integrations/buildium.py` is empty)
- Airtable integration (`integrations/airtable.py` is empty)
- RLS integration (`integrations/rls.py` is empty)
- FastAPI app initialization in `main.py` (currently placeholder)
- Database layer (`core/db.py` - planned)
- Event system (`core/events.py` - planned)
- Cache/queue (`core/cache.py` - planned)

## Data Flow Patterns

### Gmail Webhook Flow (Current)
```
Google Pub/Sub → /webhooks/gmail endpoint
  → Decode base64 message
  → Validate PubSubMessageData
  → [TODO: Process with GmailClient]
  → [TODO: Parse email content]
  → [TODO: Classify email]
  → [TODO: Store in database]
```

### Planned: Buildium ↔ Airtable Sync
```
Buildium Webhook → Event Queue
  → Fetch updated resource from Buildium
  → Compare with Airtable record
  → Push delta to Airtable or Buildium
  → Update sync state
```

### Planned: RLS Listing Integration
```
RLS API → OAuth2 Client
  → Fetch listings (OData)
  → Normalize RESO schema → Internal model
  → Persist to database
```

## Key Design Decisions

### 1. Service Account with Domain-Wide Delegation
- `GmailClient` uses Google service account JSON
- `ensure_token()` impersonates users via domain-wide delegation
- Enables multi-user email access without per-user OAuth

### 2. Pydantic Models for External APIs
- Models mirror Buildium OpenAPI schema exactly
- Field aliases handle API naming conventions (`emailAddress` → `email_address`)
- Type safety and validation at boundaries

### 3. Modular Domain Structure
- Each domain is self-contained
- Sub-domains (e.g., `property_management/accounting/`) for complex domains
- Clear separation of concerns

### 4. FastAPI Router Pattern
- Routers in `api/v1/routers/` for versioning
- Each router handles one domain area
- Planned: router registration in `main.py`

### 5. Logging Strategy
- Centralized setup in `core/logging.py`
- Module-level logger export: `from core.logging import logger`
- Consistent format: `[{time}] {level} - {name} - {message}`

## Code Style & Conventions

- **Type hints**: Required on all function signatures
- **Docstrings**: Google-style on all public functions/classes
- **File headers**: Three-line description at top of each file
- **Function length**: Max 40 lines, modules max 300 lines
- **Async**: Prefer synchronous by default, async when needed for performance
- **Git commits**: Conventional Commits format

## Integration Patterns

### Gmail Integration
- **Pattern**: Pub/Sub push notifications
- **Auth**: Service account with domain-wide delegation
- **Client**: Async HTTP client (HTTPX)
- **Flow**: Webhook → Decode → Process → Parse → Classify → Store

### Buildium Integration (Planned)
- **Pattern**: OpenAPI-based client
- **Auth**: OAuth2 authentication
- **Features**: Pagination handling, rate limiting

### Airtable Integration (Planned)
- **Pattern**: PyAirtable SDK wrapper
- **Operations**: Table-based operations, formula queries

## Missing Infrastructure (Planned)

1. **Database layer** (`core/db.py`): SQLModel + PostgreSQL
2. **Event system** (`core/events.py`): Webhook triggers, retry logic
3. **Cache/Queue** (`core/cache.py`): Redis for job queues
4. **Configuration** (`core/config.py`): Pydantic Settings for env vars

## Recommendations for AI Agents

When providing advice, consider:

1. **Domain boundaries**: Keep business logic within appropriate domains
2. **Integration layer**: External API clients should be thin wrappers
3. **Type safety**: Use Pydantic models at API boundaries
4. **Async patterns**: Use async/await for I/O operations
5. **Error handling**: Plan retry logic and error recovery
6. **Testing**: Structure supports unit tests per layer
7. **Scalability**: Vertical slices can become microservices later

This architecture supports incremental development, clear separation of concerns, and future scalability.

