## Heterogeneous Legal Dataset – Logical Data Model (Mermaid)

Below is a detailed view of the core entities, their key fields (including heterogeneous representations), and relationships.  
This focuses on the **scaled pack** but is also compatible with the smaller original pack.

```mermaid
erDiagram
    %% ======================
    %% CORE ENTITIES
    %% ======================

    CLIENT ||--o{ MATTER : "has"
    CLIENT {
        string client_id PK        "CL-10xx canonical id"
        string id                  "alt id (JSON)"
        string cid                 "alt id (XML)"
        string company_name        "primary name (CSV/XLSX)"
        string custFullNm          "name variant (JSON, upper/abbr)"
        string nm                  "name variant (XML)"
        string industry            "canonical industry"
        string sector              "lowercase variant (JSON)"
        string cat                 "XML category label"
        string annual_revenue      "CSV/XLSX, formatted currency"
        string annual_turnover     "XML numeric string"
        float  turnover            "JSON numeric"
        string contact_phone       "CSV phone, multiple formats"
        string phone               "JSON/XML phone variants"
        string created_at          "client created (CSV/XLSX)"
        string created             "client created (JSON, alt key)"
        string registered_on       "meta.registered_on, many formats"
    }

    MATTER ||--o{ BILLING_ENTRY : "billed by"
    MATTER ||--o{ DOCUMENT_META : "has"
    MATTER {
        string matter_id PK        "MAT-10xx canonical id"
        string file_no             "JSON alt id"
        string file_id             "used in billing_entries"
        string client_id FK        "links to CLIENT.client_id"
        string client_ref          "alt client FK (CSV)"
        string matterSummary       "JSON narrative title"
        string title               "CSV canonical title"
        string area                "JSON practice area"
        string practice_area       "CSV practice area"
        string startDate           "JSON start date, many formats"
        string opened_on           "CSV start date, many formats"
        string owner               "JSON responsible attorney"
        string lead_attorney       "CSV responsible attorney"
        string estimated_value     "amount with various formats"
    }

    BILLING_ENTRY {
        string entry_id PK         "BL-xxxxxx"
        string file_id FK          "FK to MATTER.matter_id"
        string att_id              "attorney identifier"
        string hours               "decimal hours as string"
        string rate                "hourly rate as string"
        string amount              "numeric or formatted currency"
        string description         "short activity label"
        string entry_date          "date with heterogeneous formats"
    }

    DOCUMENT_META {
        string doc_id PK           "D-2xxx"
        string matter_id FK        "FK to MATTER.matter_id"
        string client FK           "FK to CLIENT.client_id"
        string doc_type            "Contract / Motion / etc."
        string title               "document title"
        string created             "many date formats"
        string uploaded_by         "attorney name"
        string file_type           "pdf / docx / txt"
    }

    %% ======================
    %% TEXTUAL / DERIVED ARTEFACTS
    %% ======================

    DOCUMENT_META ||--|| DOC_TEXT : "renders as"
    MATTER       ||--o{ BILLING_FILE : "summarized in"

    DOC_TEXT {
        string doc_id FK           "from DOCUMENT_META"
        string matter_id FK        "from DOCUMENT_META"
        string client_id FK        "from DOCUMENT_META"
        string file_type           "drives filename suffix"
        text   body                "LLM-generated legal text"
    }

    BILLING_FILE {
        string matter_id FK        "from MATTER"
        string client_id FK        "from MATTER/CLIENT"
        string simulated_format    "PDF/DOCX/TXT label"
        text   header_ids          "noisy ids e.g. MTR-1010 vs MAT-1011"
        text   client_block        "noisy vs canonical client names"
        text   matter_block        "noisy vs canonical titles"
        text   embedded_entries    "denormalized view of BILLING_ENTRY"
        text   totals_block        "approx vs exact totals"
        text   narrative_summary   "LLM narrative, may conflict with structured data"
    }

    %% ======================
    %% OTHER HETEROGENEOUS SOURCES (ABSTRACTED)
    %% ======================

    EMAIL      ||--o{ MATTER : "mentions"
    REGULATION ||--o{ MATTER : "cited by"
    FILING     ||--|| MATTER : "belongs to"

    EMAIL {
        string email_id PK         "line id in emails_A.jsonl"
        string from_addr           "sender"
        string to_addr             "recipient(s)"
        string subject             "often embeds matter / client hints"
        string body                "unstructured text referencing clients/matters"
        string related_client_id   "soft link via text / heuristics"
        string related_matter_id   "soft link via text / heuristics"
    }

    REGULATION {
        string reg_id PK           "REG-30x"
        string title               "regulation heading"
        text   body                "full text"
    }

    FILING {
        string filing_id PK        "AFF- / COM- / MTD- codes"
        string matter_id FK        "FK to MATTER"
        string filing_type         "affidavit / complaint / motion"
        text   body                "filing content"
    }
```

### How to read this model

- **CLIENT**: Same real-world entity appears under multiple field names (`client_id`, `id`, `cid`, `custFullNm`, etc.), across CSV/JSON/XML/XLSX, with **value‑level inconsistencies** for revenue, phone, and dates.
- **MATTER**: Links to a single canonical client but exposes **id + date + value variations** (`matter_id` vs `file_no` vs `file_id`; `startDate` vs `opened_on`; different estimated value formats).
- **BILLING_ENTRY**: Normalized line‑items keyed by `file_id` → `MATTER.matter_id`; amounts and dates intentionally stored with mixed formats and occasional nulls.
- **DOCUMENT_META → DOC_TEXT**: Metadata row plus one or more text files; text is generated via LLM and may introduce **semantic drift** relative to structured fields.
- **BILLING_FILE**: Per‑matter narrative dossier that denormalizes and **adds noise** to CLIENT/MATTER/BILLING_ENTRY (id aliasing, drifted names/titles, approximate totals).
- **EMAIL / REGULATION / FILING**: Additional unstructured/semistructured sources that reference CLIENT/MATTER either via hard FK (`matter_id`) or via soft textual hints; useful for entity‑resolution and cross‑source fusion.

Use this diagram as the orchestration blueprint: ingest each entity type, normalize identifiers (client/matter ids), then layer value normalization (dates, phones, currency) and semantic alignment (titles, descriptions, narratives) on top.







