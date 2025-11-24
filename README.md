# INTERNAL DEV README

> 📖 **For detailed architecture and design documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**

Perfect — that's the smartest scope possible. Those three "vertical slices" are the backbone of your internal ecosystem and each represents a distinct *integration-to-domain-to-interface* flow.

Here’s what we’ll visualize in the C4-style breakdown:

---

## 🧠 Context — What Each Slice Does

| Slice                        | Core Function                                                                                            | Data Direction                              |
| ---------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| **Airtable ↔ Buildium Sync** | Keeps financial and property data aligned between Buildium and your internal Airtable “PM Balance Sheet” | Bi-directional (webhook + reconciliation)   |
| **RLS Listing Integration**  | Pulls listings + media from CoreLogic Trestle (RESO Web API) and maps to your internal `listings` schema | One-way ingest (RLS → DB)                   |
| **Gmail Manager**            | Parses inbound agent/client emails for CRM enrichment, task triggers, and communication tracking         | One-way ingest (Gmail → queue → CRM/events) |

---

## 🏗️ C4-Style Phase 1 MVP Architecture (Textual Diagram)

```
                     ┌────────────────────────┐
                     │       Wonder Street    │
                     │   Internal Platform    │
                     └────────────┬───────────┘
                                  │
                     ┌────────────┼────────────┐
                     │            │            │
           Airtable↔Buildium   RLS Listings   Gmail Manager
            Sync Service        Ingestion      Automation
                     │            │            │
                     ▼            ▼            ▼
   ┌────────────────────────┐ ┌────────────────────────┐ ┌────────────────────────┐
   │ domains/               │ │ domains/               │ │ domains/               │
   │ property_management/   │ │ listings/              │ │ email/                 │
   │   ├─ sync.py           │ │   ├─ integrations.py   │ │   ├─ ingestion.py      │
   │   ├─ models.py         │ │   ├─ models.py         │ │   ├─ parsing.py        │
   │   └─ services.py       │ │   └─ services.py       │ │   └─ classification.py │
   └────────────┬───────────┘ └────────────┬───────────┘ └────────────┬───────────┘
                │                          │                           │
                ▼                          ▼                           ▼
     ┌────────────────┐        ┌────────────────────┐       ┌──────────────────┐
     │ integrations/  │        │ integrations/      │       │ integrations/    │
     │   buildium.py  │        │   rls.py           │       │   gmail.py       │
     │   airtable.py  │        └────────────────────┘       └──────────────────┘
     └───────┬────────┘
             │
             ▼
   ┌──────────────────────┐
   │ core/                │
   │   db.py              │   ← SQLModel + Postgres
   │   events.py          │   ← Event bus / async triggers
   │   cache.py           │   ← Redis / job queue
   │   logging.py         │
   └──────────────────────┘
```

---

## 🧩 C4 Breakdown by Level

### **C1 – System Context**

Wonder Street Platform connects:

* Buildium (Property & Lease data)
* Airtable (PM Balance Sheet)
* RLS / CoreLogic (MLS Listings)
* Gmail (communications feed)
  to a unified operational backend (FastAPI + SQLModel).

---

### **C2 – Container Level**

| Container               | Tech                                 | Description                                                         |
| ----------------------- | ------------------------------------ | ------------------------------------------------------------------- |
| **FastAPI app**         | Python (Uvicorn)                     | Hosts REST endpoints, event listeners, and internal API calls.      |
| **PostgreSQL**          | SQLModel ORM                         | Stores listings, sync states, tenant/lease records, and audit logs. |
| **Redis / Cache Layer** | Redis / RQ                           | Queue for webhook + email event processing.                         |
| **External Services**   | Buildium, Airtable, CoreLogic, Gmail | Source systems for syncs and event triggers.                        |

---

### **C3 – Component Level**

#### 🧮 Airtable ↔ Buildium Sync

* **integrations/buildium.py** — API client for Buildium (auth, pagination, rate-limit handling).
* **integrations/airtable.py** — Wrapper for pyAirtable SDK.
* **domains/property_management/sync.py** — Orchestrates data reconciliation:

  1. Buildium webhook event → async queue
  2. Fetch updated resource (lease, transaction)
  3. Compare with Airtable record
  4. Push delta → Airtable or Buildium as needed
* **core/events.py** — Handles webhook triggers and retry logic.

#### 🏙️ RLS Listing Integration

* **integrations/rls.py** — OAuth2 + OData client for Trestle API.
* **domains/listings/integrations.py** — Pulls listings, photos, metadata.
* **domains/listings/services.py** — Normalizes RESO schema → internal listing model.
* **core/db.py** — Persist listings and media.
* (Optional later) sync job in **core/events.py** for periodic refresh.

#### 📬 Gmail Manager

* **integrations/gmail.py** — Google Pub/Sub listener (new emails).
* **domains/email/ingestion.py** — Receives raw email payload → queue.
* **domains/email/parsing.py** — Extracts structured data (sender, subject, body, thread).
* **domains/email/classification.py** — ML or rule-based tagging (lead, client, spam).
* **domains/crm/services.py** (later) — Links messages to contacts/leads.

---

### **C4 – Code/Module Level (Simplified Directory)**

```
app/
├── api/
│   └── v1/
│       └── routers/
│           ├── property_management.py
│           ├── listings.py
│           └── email.py
│
├── domains/
│   ├── property_management/
│   │   ├── models.py
│   │   ├── sync.py
│   │   └── services.py
│   │
│   ├── listings/
│   │   ├── models.py
│   │   ├── integrations.py
│   │   └── services.py
│   │
│   └── email/
│       ├── ingestion.py
│       ├── parsing.py
│       └── classification.py
│
├── integrations/
│   ├── buildium.py
│   ├── airtable.py
│   ├── rls.py
│   └── gmail.py
│
├── core/
│   ├── db.py
│   ├── events.py
│   ├── logging.py
│   └── cache.py
│
└── main.py
```

---

## 🎯 Why This is the Sweet Spot

* **Single layer of integration per slice** → fewer context switches.
* **Event-driven backbone** (via `core/events.py`) supports future automation.
* **Reflex-friendly**: you can later add a dashboard per slice without restructuring backend.
* **Scalable to microservices** later by moving each domain to its own container if needed.

---

