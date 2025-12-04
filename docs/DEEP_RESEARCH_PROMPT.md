# Data Fusion Knowledge Engine: Dataset Architecture & Query Routing System

## Executive Summary

You are analyzing a **heterogeneous legal dataset** designed to test and demonstrate **data fusion** and **entity resolution** capabilities using AI . The ultimate goal is to build a **Knowledge Engine** that dynamically routes natural language queries to appropriate data segments across multiple heterogeneous sources **without pre-transforming entire datasets**. Instead, the system uses a **data map** that specifies: (1) which data source to query, (2) which fields are relevant, and (3) how to format/interpret the data for downstream reasoning.

This prompt provides complete ground truth about the dataset structure, relationships, and the intended system architecture.

---

## Part 1: Dataset Inventory & Structure

### 1.1 Core Structured Datasets

#### **Client Records (4 Formats, Same Entity Type)**

**File: `structured_clients_A.csv`**
- **Format**: CSV (comma-separated)
- **Primary Key**: `client_id` (format: `CL-10xx`, e.g., `CL-1001`)
- **Fields**:
  - `client_id`: Unique identifier (canonical)
  - `company_name`: Client company name (e.g., "Stonebridge Motors Inc")
  - `industry`: Industry classification (e.g., "Automotive", "Healthcare", "Finance")
  - `annual_revenue`: Revenue as formatted currency string (e.g., `"$12,000,000"`)
  - `contact_phone`: Phone number in format `(555) 125-5506`
  - `created_at`: Date in format `2022-09-25`
- **Row Count**: 2000+ (scaled version)
- **Purpose**: Primary client data source in flat CSV format

**File: `structured_clients_B.json`**
- **Format**: JSON (nested structure)
- **Primary Key**: `id` (same value as `client_id` from CSV, but different field name)
- **Structure**: Array of objects
- **Fields**:
  - `id`: Client identifier (e.g., `"CL-1001"`) - **maps to CSV `client_id`**
  - `custFullNm`: Company name in UPPERCASE or abbreviated (e.g., `"STONEBRIDGE MOTORS INC"` or `"Nimbus Soft"`) - **semantic variant of `company_name`**
  - `sector`: Industry in lowercase (e.g., `"automotive"`) - **maps to CSV `industry`**
  - `financials.turnover`: Revenue as numeric integer (e.g., `12000000`) - **maps to CSV `annual_revenue`**
  - `financials.currency`: Always `"USD"`
  - `phone`: Phone in format `"+1-555-338-9279"` or `null` - **maps to CSV `contact_phone`**
  - `meta.registered_on`: Date in various formats (e.g., `"22-Jul-2017"`, `"1583625600"` Unix timestamp) - **maps to CSV `created_at`**
- **Row Count**: 2000+ (same clients as CSV, different representation)
- **Purpose**: Same entities as CSV but with schema variations and value format differences

**File: `structured_clients_C.xml`**
- **Format**: XML (hierarchical)
- **Primary Key**: `cid` attribute on `<Entity>` element (e.g., `cid="CL-1001"`)
- **Structure**: `<Clients><Entity cid="...">...</Entity></Clients>`
- **Fields** (as XML elements):
  - `cid`: Client identifier attribute - **maps to CSV `client_id`**
  - `<nm>`: Company name (e.g., `"Stonebridge Motors Inc"`) - **maps to CSV `company_name`**
  - `<annual_turnover>`: Revenue as numeric string (e.g., `"12000000"`) - **maps to CSV `annual_revenue`**
  - `<cat>`: Industry category (e.g., `"Automotive"`) - **maps to CSV `industry`**
  - `<phone>`: Phone in format `"555.697.7543"` - **maps to CSV `contact_phone`**
- **Row Count**: 2000+ (same clients, XML representation)
- **Purpose**: Same entities in XML format with different field names

**File: `structured_clients_D.xlsx`**
- **Format**: Excel spreadsheet
- **Primary Key**: `cust_code` (e.g., `CL-1001`) - **maps to CSV `client_id`**
- **Fields**:
  - `cust_code`: Client identifier - **maps to CSV `client_id`**
  - `clientName`: Company name - **maps to CSV `company_name`**
  - `industry`: Industry - **maps to CSV `industry`**
  - `revenue`: Revenue (numeric or formatted) - **maps to CSV `annual_revenue`**
  - `phone`: Phone number - **maps to CSV `contact_phone`**
  - `created`: Creation date - **maps to CSV `created_at`**
- **Row Count**: 2000+ (same clients, Excel format)
- **Purpose**: Same entities in spreadsheet format with different field names

**Key Insight**: All four files represent the **same set of clients** but with:
- **Schema variations**: `client_id` vs `id` vs `cid` vs `cust_code`
- **Field name variations**: `company_name` vs `custFullNm` vs `nm` vs `clientName`
- **Value format variations**: `"$12,000,000"` vs `12000000` vs `"12000000"`
- **Date format variations**: `"2022-09-25"` vs `"22-Jul-2017"` vs `"1583625600"`
- **Phone format variations**: `"(555) 125-5506"` vs `"+1-555-338-9279"` vs `"555.489.2584"`

---

#### **Matter Records (2 Formats, Same Entity Type)**

**File: `matters_A.csv`**
- **Format**: CSV
- **Primary Key**: `matter_id` (format: `MAT-10xx`, e.g., `MAT-1011`)
- **Fields**:
  - `matter_id`: Unique matter identifier (canonical)
  - `client_ref`: Foreign key to client (e.g., `"CL-1001"`) - **links to `structured_clients_A.csv.client_id`**
  - `title`: Matter title/description (e.g., `"Stonebridge Motors Inc - Master Services Agreement Negotiation"`)
  - `practice_area`: Legal practice area (e.g., `"IP"`, `"Employment"`, `"Contracts"`)
  - `opened_on`: Matter start date in various formats (e.g., `"03-Apr-2021"`, `"2024-01-24"`, `"28/03/19"`)
  - `lead_attorney`: Attorney name (e.g., `"Daniel Park"`, `"Hannah Lee"`)
  - `estimated_value`: Estimated matter value in various formats (e.g., `"12000"`, `"$12,000"`, `"12K"`, `"€10,800"`)
- **Row Count**: 2000+ (scaled version)
- **Purpose**: Primary matter/case data source

**File: `matters_B.json`**
- **Format**: JSON (flat structure)
- **Primary Key**: `file_no` (same value as `matter_id` from CSV, but different field name)
- **Structure**: Array of objects
- **Fields**:
  - `file_no`: Matter identifier (e.g., `"MAT-1011"`) - **maps to CSV `matter_id`**
  - `client_id`: Foreign key to client (e.g., `"CL-1001"`) - **maps to CSV `client_ref`**
  - `matterSummary`: Matter description (e.g., `"Stonebridge Motors Inc - Master Services Agreement Negotiation"`) - **semantic variant of `title`**
  - `area`: Practice area (e.g., `"IP"`, `"Regulatory"`) - **maps to CSV `practice_area`**
  - `startDate`: Start date in various formats (e.g., `"2017-08-23"`, `"22/08/22"`, `"1566432000"` Unix, or `null`) - **maps to CSV `opened_on`**
  - `owner`: Attorney name (e.g., `"Daniel Park"`) - **maps to CSV `lead_attorney`**
- **Row Count**: 2000+ (same matters as CSV, different representation)
- **Purpose**: Same entities as CSV with schema and value format variations

**Key Insight**: Both files represent the **same set of matters** but with:
- **Schema variations**: `matter_id` vs `file_no`, `client_ref` vs `client_id`, `title` vs `matterSummary`, `practice_area` vs `area`, `lead_attorney` vs `owner`, `opened_on` vs `startDate`
- **Value format variations**: Dates in multiple formats, practice areas may have slight variations

---

#### **Billing Entry Records**

**File: `billing_entries_A.csv`**
- **Format**: CSV
- **Primary Key**: `entry_id` (format: `BL-xxxxxx`, e.g., `BL-831876`)
- **Foreign Key**: `file_id` (e.g., `"MAT-1011"`) - **links to `matters_A.csv.matter_id` or `matters_B.json.file_no`**
- **Fields**:
  - `entry_id`: Unique billing entry identifier
  - `file_id`: Matter identifier (foreign key) - **must resolve to matter_id/file_no**
  - `att_id`: Attorney identifier (e.g., `"AT-005"`)
  - `hours`: Hours billed as decimal string (e.g., `"7.1"`)
  - `rate`: Hourly rate as string (e.g., `"250"`, `"375.00"`)
  - `amount`: Billing amount in various formats (e.g., `"1775.0"`, `"$1,675.00"`, `""` (empty/missing))
  - `description`: Work description (e.g., `"Reviewed contract"`, `"Drafted motion"`, `"Prepared discovery"`, `"Client call"`)
  - `entry_date`: Date in various formats (e.g., `"29/02/20"`, `"2019-07-28"`, `"1663804800"` Unix timestamp)
- **Row Count**: 2000+ (scaled version)
- **Purpose**: Line-item billing records linked to matters
- **Relationship**: Many billing entries per matter (one-to-many)

---

#### **Document Metadata**

**File: `document_metadata.json`**
- **Format**: JSON (flat array)
- **Primary Key**: `doc_id` (format: `D-2xxx`, e.g., `D-2000`)
- **Foreign Keys**: 
  - `matter_id` (e.g., `"MAT-1042"`) - **links to `matters_A.csv.matter_id` or `matters_B.json.file_no`**
  - `client` (e.g., `"CL-1005"`) - **links to any client file's identifier fields**
- **Fields**:
  - `doc_id`: Unique document identifier
  - `matter_id`: Matter identifier (foreign key)
  - `client`: Client identifier (foreign key)
  - `doc_type`: Document type (e.g., `"Contract"`, `"Agreement"`, `"Motion"`, `"Brief"`)
  - `title`: Document title (e.g., `"Master Services Agreement"`)
  - `created`: Creation date in various formats (e.g., `"15/08/24"`, `"1650844800"` Unix, `"2020-08-30"`)
  - `uploaded_by`: Attorney name (e.g., `"Ayesha Khan"`)
  - `file_type`: File format indicator (e.g., `"pdf"`, `"docx"`, `"txt"`)
- **Row Count**: 2000+ (scaled version)
- **Purpose**: Metadata for legal documents
- **Relationship**: Many documents per matter, many documents per client

---

### 1.2 Textual/Derived Datasets

#### **Document Text Files**

**Files: `documents/D-{doc_id}_{file_type}.txt`**
- **Format**: Plain text (extracted from PDF/DOCX or native TXT)
- **Naming Pattern**: `D-{doc_id}_{file_type}.txt` (e.g., `D-2000_pdf.txt`, `D-2001_txt.txt`, `D-2006_docx.txt`)
- **Content**: Full text content of legal documents (LLM-generated in scaled version)
- **Linkage**: `doc_id` in filename matches `document_metadata.json.doc_id`
- **Purpose**: Full-text content for semantic search and document analysis
- **Count**: 2000+ files (one per document metadata entry)

---

#### **Billing Narrative Files**

**Files: `billing_files/{matter_id}.txt`**
- **Format**: Plain text (structured narrative)
- **Naming Pattern**: `{matter_id}.txt` (e.g., `MAT-1011.txt`)
- **Content Structure**:
  - Header with **noisy/inconsistent IDs** (e.g., `matter_id: MTR-1010` when actual matter is `MAT-1011`)
  - Client information block with **name variations** (e.g., `client_name: Stonebridge Motors Company` vs canonical `Stonebridge Motors Inc`)
  - Matter information with **title variations** (e.g., narrative: `"framework commercial arrangement Negotiation"` vs structured: `"Master Services Agreement Negotiation"`)
  - Embedded billing entries (denormalized view of `billing_entries_A.csv`)
  - Narrative summary (LLM-generated text that may conflict with structured data)
- **Linkage**: Filename `{matter_id}` should match `matters_A.csv.matter_id`, but header may contain aliases
- **Purpose**: Human-readable billing summaries with intentional inconsistencies for testing entity resolution
- **Count**: 2000+ files (one per matter, approximately)

---

#### **Email Records**

**File: `emails_A.jsonl`**
- **Format**: JSON Lines (one JSON object per line)
- **Fields** (per line):
  - `email_id`: Unique email identifier
  - `from_addr`: Sender email address
  - `to_addr`: Recipient email address(es)
  - `subject`: Email subject line (often contains matter/client references)
  - `body`: Email body text (unstructured, may mention clients/matters)
  - `related_client_id`: **Soft link** - inferred from text, may be `null` or incorrect
  - `related_matter_id`: **Soft link** - inferred from text, may be `null` or incorrect
- **Purpose**: Email correspondence with soft links to clients/matters via text analysis
- **Relationship**: Many-to-many with clients and matters (via soft linking)

---

#### **Regulation Files**

**Files: `regulations/REG-{number}.txt`**
- **Format**: Plain text
- **Naming Pattern**: `REG-{number}.txt` (e.g., `REG-300.txt`)
- **Content**: Full text of legal regulations
- **Purpose**: Reference regulations that may be cited in matters
- **Relationship**: Soft link to matters (via text search in matter titles/descriptions)

---

#### **Filing Files**

**Files: `documents/filings/{type}-{number}.txt`**
- **Format**: Plain text
- **Naming Pattern**: `{type}-{number}.txt` where type is `AFF-` (affidavit), `COM-` (complaint), or `MTD-` (motion)
- **Content**: Full text of court filings
- **Purpose**: Court filing documents
- **Relationship**: Hard link to matters via `matter_id` in some cases, or soft link via text

---

## Part 2: Dataset Relationships & Linkage

### 2.1 Entity Relationship Diagram

```
CLIENT (1) ──< (many) MATTER (1) ──< (many) BILLING_ENTRY
                │
                │ (1) ──< (many) DOCUMENT_META ──> (1) DOC_TEXT
                │
                │ (1) ──< (many) BILLING_FILE
                │
                │ (many) ──< (many) EMAIL (soft link)
                │
                │ (many) ──< (many) REGULATION (soft link)
                │
                └──< (many) FILING
```

### 2.2 Hard Foreign Key Relationships

**Client → Matter:**
- `matters_A.csv.client_ref` → `structured_clients_A.csv.client_id`
- `matters_B.json.client_id` → `structured_clients_B.json.id`
- **Challenge**: Must resolve `client_ref`/`client_id` across all 4 client formats using entity resolution

**Matter → Billing Entry:**
- `billing_entries_A.csv.file_id` → `matters_A.csv.matter_id` OR `matters_B.json.file_no`
- **Challenge**: `file_id` must match either `matter_id` or `file_no` (same value, different field names)

**Matter → Document:**
- `document_metadata.json.matter_id` → `matters_A.csv.matter_id` OR `matters_B.json.file_no`
- **Challenge**: Same as above - field name variation

**Document → Client:**
- `document_metadata.json.client` → Any client identifier field (`client_id`, `id`, `cid`, `cust_code`)
- **Challenge**: Must resolve across all 4 client formats

**Matter → Billing File:**
- `billing_files/{matter_id}.txt` filename → `matters_A.csv.matter_id`
- **Challenge**: File header may contain **noisy alias** (e.g., `MTR-1010` instead of `MAT-1011`)

### 2.3 Soft Link Relationships

**Email → Client/Matter:**
- `emails_A.jsonl.related_client_id` and `related_matter_id` are **inferred from text**
- May be `null`, incorrect, or require NLP to extract
- **Challenge**: Text analysis needed to establish links

**Regulation → Matter:**
- No explicit foreign key
- **Challenge**: Text search in matter titles/descriptions to find regulation references

**Filing → Matter:**
- Some filings have explicit `matter_id` in content
- Others require text matching
- **Challenge**: Mixed hard/soft linking

### 2.4 Entity Resolution Challenges

**Same Entity, Different Identifiers:**
- Client: `CL-1001` = `id:"CL-1001"` = `cid="CL-1001"` = `cust_code:"CL-1001"` (same value, different field names)
- Matter: `MAT-1011` = `file_no:"MAT-1011"` = `file_id:"MAT-1011"` (same value, different field names)
- **But also**: `MAT-1011` may appear as `MTR-1010` in billing file headers (intentional noise)

**Same Entity, Different Representations:**
- Client name: `"Stonebridge Motors Inc"` = `"STONEBRIDGE MOTORS INC"` = `"Stonebridge Motors Company"` (semantic variants)
- Matter title: `"Master Services Agreement Negotiation"` = `"framework commercial arrangement Negotiation"` (semantic variants)
- **Challenge**: Requires semantic matching, not just exact string matching

---

## Part 3: Value Format Heterogeneity

### 3.1 Date Formats (Found Across Multiple Fields)

**Examples:**
- ISO format: `"2022-09-25"`
- DD/MM/YY: `"15/09/22"`
- DD/MM/YYYY: `"25/09/2023"`
- DD-Mon-YYYY: `"25-Oct-2021"`
- DD-Mon-YY: `"03-Apr-2021"`
- Unix timestamp: `"1650844800"` or `1650844800` (as integer)
- DD/MM/YY (alternative): `"28/03/19"`

**Fields Affected:**
- Client: `created_at`, `created`, `registered_on`, `meta.registered_on`
- Matter: `opened_on`, `startDate`
- Billing: `entry_date`
- Document: `created`

**Normalization Requirement**: All dates must be converted to a single canonical format (e.g., ISO `YYYY-MM-DD`) for temporal queries and comparisons.

---

### 3.2 Currency/Numeric Formats

**Examples:**
- Formatted currency: `"$12,000,000"`, `"$1,675.00"`, `"€10,800"`
- Numeric string: `"12000000"`, `"1775.0"`
- Numeric integer: `12000000` (in JSON)
- Abbreviated: `"12K"`
- Quoted string: `'"$1,675.00"'` (with outer quotes)

**Fields Affected:**
- Client: `annual_revenue`, `annual_turnover`, `turnover`, `financials.turnover`, `revenue`
- Matter: `estimated_value`
- Billing: `amount`, `rate`

**Normalization Requirement**: All currency values must be converted to a single numeric format (e.g., float) for mathematical operations and comparisons.

---

### 3.3 Phone Number Formats

**Examples:**
- Parentheses: `"(555) 125-5506"`
- International: `"+1-555-338-9279"`
- Dots: `"555.489.2584"`
- Dashes: `"555-125-5506"`
- Null/missing: `null`, `"N/A"`, empty string

**Fields Affected:**
- Client: `contact_phone`, `phone`

**Normalization Requirement**: All phone numbers should be converted to a canonical format (e.g., E.164: `+15551255506`) for matching and deduplication.

---

### 3.4 Industry/Sector Variations

**Examples:**
- Canonical: `"Automotive"`, `"Healthcare"`, `"Finance"`
- Lowercase: `"automotive"`, `"healthcare"`, `"finance"`
- Abbreviated: `"Tech"` vs `"Technology"`

**Fields Affected:**
- Client: `industry`, `sector`, `cat`

**Normalization Requirement**: Industry values should be normalized to a canonical set (case-insensitive matching, abbreviation expansion).

---

## Part 4: Project Goal & Architecture

### 4.1 End Goal: Data Fusion Knowledge Engine

**Objective**: Build a **Knowledge Engine** that accepts natural language queries and dynamically routes them to the appropriate data segments across heterogeneous sources **without pre-transforming entire datasets**.

**Key Principles:**
1. **No Pre-Transformation**: Do not reshape entire datasets into a unified schema upfront
2. **Dynamic Routing**: Map queries to specific data sources and fields at query time
3. **On-Demand Normalization**: Normalize values only when needed for the specific query
4. **Semantic Understanding**: Understand that `client_id`, `id`, `cid`, `cust_code` all refer to the same concept
5. **Value Interpretation**: Understand that `"$12,000,000"` and `12000000` represent the same value

---

### 4.2 Data Map Architecture

The **Data Map** is the core component that enables query routing. It contains:

#### **4.2.1 Schema Mapping**
Maps semantic concepts to field names across sources:

```json
{
  "client_identifier": {
    "concept": "unique client ID",
    "fields": {
      "structured_clients_A.csv": "client_id",
      "structured_clients_B.json": "id",
      "structured_clients_C.xml": "cid",
      "structured_clients_D.xlsx": "cust_code"
    },
    "value_equivalence": "same value, different field names"
  },
  "client_name": {
    "concept": "client company name",
    "fields": {
      "structured_clients_A.csv": "company_name",
      "structured_clients_B.json": "custFullNm",
      "structured_clients_C.xml": "nm",
      "structured_clients_D.xlsx": "clientName"
    },
    "semantic_equivalence": "may have case/abbreviation variations"
  },
  "client_revenue": {
    "concept": "annual revenue/turnover",
    "fields": {
      "structured_clients_A.csv": "annual_revenue",
      "structured_clients_B.json": "financials.turnover",
      "structured_clients_C.xml": "annual_turnover",
      "structured_clients_D.xlsx": "revenue"
    },
    "format_variations": ["currency_string", "numeric_integer", "numeric_string"],
    "normalization_rule": "strip_currency_symbols_and_commas_to_float"
  }
}
```

#### **4.2.2 Entity Resolution Rules**
Defines how to match entities across sources:

```json
{
  "client_resolution": {
    "primary_key_fields": ["client_id", "id", "cid", "cust_code"],
    "matching_strategy": "exact_value_match",
    "semantic_fallback": {
      "name_fields": ["company_name", "custFullNm", "nm", "clientName"],
      "similarity_threshold": 0.85,
      "normalization": ["case_insensitive", "abbreviation_expansion"]
    }
  },
  "matter_resolution": {
    "primary_key_fields": ["matter_id", "file_no", "file_id"],
    "matching_strategy": "exact_value_match",
    "noise_handling": {
      "alias_patterns": ["MTR-{num} -> MAT-{num}"],
      "fuzzy_matching": true
    }
  }
}
```

#### **4.2.3 Value Normalization Rules**
Defines how to interpret and convert values:

```json
{
  "date_normalization": {
    "input_formats": [
      "YYYY-MM-DD",
      "DD/MM/YY",
      "DD/MM/YYYY",
      "DD-Mon-YYYY",
      "DD-Mon-YY",
      "unix_timestamp"
    ],
    "output_format": "YYYY-MM-DD",
    "parsing_rules": "standard_date_parsing_with_fallback"
  },
  "currency_normalization": {
    "input_formats": [
      "currency_string_with_symbols",
      "numeric_string",
      "numeric_integer",
      "abbreviated_string"
    ],
    "output_format": "float",
    "parsing_rules": "strip_symbols_commas_quotes_convert_to_float"
  },
  "phone_normalization": {
    "input_formats": [
      "(XXX) XXX-XXXX",
      "+1-XXX-XXX-XXXX",
      "XXX.XXX.XXXX",
      "XXX-XXX-XXXX"
    ],
    "output_format": "E.164",
    "parsing_rules": "extract_digits_add_country_code"
  }
}
```

#### **4.2.4 Relationship Mapping**
Defines how entities link together:

```json
{
  "client_to_matter": {
    "source_fields": {
      "matters_A.csv": "client_ref",
      "matters_B.json": "client_id"
    },
    "target_fields": {
      "structured_clients_A.csv": "client_id",
      "structured_clients_B.json": "id",
      "structured_clients_C.xml": "cid",
      "structured_clients_D.xlsx": "cust_code"
    },
    "join_strategy": "entity_resolution_then_join"
  },
  "matter_to_billing": {
    "source_fields": {
      "billing_entries_A.csv": "file_id"
    },
    "target_fields": {
      "matters_A.csv": "matter_id",
      "matters_B.json": "file_no"
    },
    "join_strategy": "exact_match_with_field_name_resolution"
  }
}
```

---

### 4.3 Query Routing Process

**Step 1: Query Analysis**
- Parse natural language query
- Identify semantic concepts (e.g., "client revenue", "matter timeline", "attorney workload")
- Extract filters/constraints (e.g., "Healthcare industry", "2023", "Daniel Park")

**Step 2: Data Map Lookup**
- For each concept, find relevant fields in data map
- Identify which data sources contain the concept
- Determine required normalization rules

**Step 3: Source Selection**
- Select optimal data sources (may use multiple for redundancy/validation)
- Identify join paths between sources
- Determine entity resolution requirements

**Step 4: Field Extraction**
- Extract only relevant fields (not entire datasets)
- Apply normalization rules on-the-fly
- Resolve entities across sources

**Step 5: Query Execution**
- Join data segments using resolved entities
- Apply filters with normalized values
- Aggregate/transform as needed
- Return results

**Example Query Flow:**
```
Query: "Show me total revenue for Healthcare clients"

1. Concepts identified: "revenue" (client_revenue), "Healthcare" (industry filter)
2. Data map lookup:
   - client_revenue → structured_clients_A.csv.annual_revenue, 
                      structured_clients_B.json.financials.turnover, etc.
   - industry → structured_clients_A.csv.industry, 
                structured_clients_B.json.sector, etc.
3. Source selection: Use structured_clients_A.csv (has both fields)
4. Field extraction: Extract only "client_id", "annual_revenue", "industry"
5. Normalization: Convert "annual_revenue" to float, normalize "industry" to canonical
6. Filter: industry = "Healthcare" (case-insensitive)
7. Aggregate: SUM(revenue) GROUP BY client_id
8. Return: Results
```

---

## Part 5: Intentional Heterogeneity (Design Feature)

### 5.1 Why Heterogeneity Exists

This dataset is **intentionally heterogeneous** to:
1. **Test Schema Matching**: Algorithms must identify that `client_id` = `id` = `cid` = `cust_code`
2. **Test Entity Resolution**: Systems must link `MAT-1011` with `MTR-1010` (noisy alias)
3. **Test Value Normalization**: Systems must understand `"$12,000,000"` = `12000000`
4. **Test Semantic Matching**: Systems must match `"Stonebridge Motors Inc"` ≈ `"STONEBRIDGE MOTORS INC"` ≈ `"Stonebridge Motors Company"`
5. **Test Conflict Resolution**: Same entity may have conflicting values across sources
6. **Test Soft Linking**: Email-to-matter links require NLP, not just foreign keys

### 5.2 Heterogeneity Categories

**Schema-Level:**
- Same concept, different field names (`client_id` vs `id` vs `cid`)
- Same concept, different structures (flat CSV vs nested JSON vs hierarchical XML)

**Value-Level:**
- Same value, different formats (dates, currency, phone numbers)
- Same entity, different representations (name variations, title variations)

**ID-Level:**
- Same entity, different identifier formats (`MAT-1011` vs `MTR-1010`)
- Intentional noise in narrative files

**Semantic-Level:**
- Same meaning, different wording ("Master Services Agreement" vs "framework commercial arrangement")
- Requires embedding-based or LLM-based matching

---

## Part 6: Query Examples & Routing Requirements

### Example Query 1: "Show me all clients in the Healthcare industry with their revenue"

**Required Data Map Lookups:**
- Concept "industry" → fields: `structured_clients_A.csv.industry`, `structured_clients_B.json.sector`, `structured_clients_C.xml.cat`
- Concept "revenue" → fields: `structured_clients_A.csv.annual_revenue`, `structured_clients_B.json.financials.turnover`, `structured_clients_C.xml.annual_turnover`
- Concept "client" → identifier fields: `client_id`, `id`, `cid`, `cust_code`

**Routing Decision:**
- Use `structured_clients_A.csv` (has both industry and revenue in one source)
- OR use `structured_clients_B.json` (has sector and turnover)
- OR join multiple sources for validation

**Normalization Required:**
- Industry: `"Healthcare"` = `"healthcare"` (case-insensitive)
- Revenue: `"$5,800,000"` → `5800000.0` (currency to float)

**Entity Resolution:**
- Not needed (single source query)

---

### Example Query 2: "Find all billing entries for matters handled by Daniel Park"

**Required Data Map Lookups:**
- Concept "attorney" → fields: `matters_A.csv.lead_attorney`, `matters_B.json.owner`
- Concept "billing" → source: `billing_entries_A.csv`
- Concept "matter" → identifier fields: `matter_id`, `file_no`, `file_id`

**Routing Decision:**
- Join `matters_A.csv` (or `matters_B.json`) with `billing_entries_A.csv`
- Match `matters_A.csv.lead_attorney` = "Daniel Park" OR `matters_B.json.owner` = "Daniel Park"
- Join on `matters_A.csv.matter_id` = `billing_entries_A.csv.file_id` OR `matters_B.json.file_no` = `billing_entries_A.csv.file_id`

**Normalization Required:**
- Attorney name: Exact match (no normalization needed)

**Entity Resolution:**
- `matter_id` = `file_no` = `file_id` (same value, different field names)
- Must resolve across matter sources

---

### Example Query 3: "Show me documents created in 2023 for Technology clients"

**Required Data Map Lookups:**
- Concept "document" → source: `document_metadata.json`
- Concept "date" → field: `document_metadata.json.created` (multiple formats)
- Concept "industry" → fields: client sources (`industry`, `sector`, `cat`)
- Concept "client" → identifier fields across all client sources

**Routing Decision:**
- Join `document_metadata.json` with client sources
- Filter `document_metadata.json.created` in 2023 (normalize dates first)
- Filter client industry = "Technology" (normalize industry first)
- Join on `document_metadata.json.client` = any client identifier field

**Normalization Required:**
- Date: Multiple formats → `YYYY-MM-DD`, then filter year = 2023
- Industry: `"Technology"` = `"technology"` (case-insensitive)

**Entity Resolution:**
- `document_metadata.json.client` must match `client_id`/`id`/`cid`/`cust_code`
- Industry must match across `industry`/`sector`/`cat`

---

## Part 7: Data Map Specification Requirements

The data map must enable the system to answer:

1. **"Where is concept X stored?"**
   - List all data sources and field names for the concept

2. **"How do I interpret value Y?"**
   - Apply appropriate normalization rule based on source and field

3. **"How do I link entity A to entity B?"**
   - Use relationship mapping to find join paths

4. **"What are the semantic variants of term Z?"**
   - Use semantic matching rules for name/title variations

5. **"Which source is best for query Q?"**
   - Consider completeness, format, and join complexity

---

## Part 8: Design Instructions for Deep Research

### Your Primary Task

Your primary objective is to **design a scalable, AI-assisted data fusion and query-routing solution**, not merely to describe the datasets.

You should propose a **concrete system architecture and strategy** that:

1. **Uses AI / LLMs where they add clear value**, and falls back to traditional methods where they are sufficient.
2. **Scales to large datasets** (thousands to millions of rows per table, many tables, many queries).
3. **Works at query time** (dynamic routing, on-demand normalization) rather than relying on full upfront transformation.
4. **Is robust to heterogeneity and noise** (schema, value, ID, and semantic inconsistencies described above).

To get there, you will still need to understand the datasets, but **dataset analysis is a means, not the end**. The end goal is a **practical, implementable design** for the Knowledge Engine.

### Design & Reasoning Objectives

Your work should:

1. **Propose an overall architecture** for the Knowledge Engine  
   - How components (parsers, data map, LLMs, vector indexes, execution engine) fit together.  
   - Where AI/LLMs are used vs. where deterministic logic is used.

2. **Define the role of AI / LLMs** in this system  
   - For example: schema matching, semantic equivalence, soft-link inference (emails → matters), conflict resolution suggestions, query interpretation, etc.  
   - When to rely on embeddings vs. full LLM calls vs. symbolic logic.

3. **Specify the data map design** that enables dynamic query routing  
   - How concepts map to fields and sources.  
   - How transformation/normalization rules are encoded.  
   - How relationship/join paths are represented.

4. **Describe the end-to-end query routing flow**  
   - From natural language query → semantic parse → data map lookup → source selection → on-demand normalization → execution → reasoning over results.  
   - How AI assists at each stage (or not).

5. **Detail strategies for handling heterogeneity at scale**  
   - Schema heterogeneity (field-name differences).  
   - Value heterogeneity (dates, currency, phones).  
   - ID heterogeneity and noise (MAT vs MTR, client IDs).  
   - Semantic heterogeneity (names, titles, narratives).

6. **Identify which parts can be solved with traditional techniques**  
   - E.g., deterministic parsing, regex, SQL joins, type conversions.  
   - And which parts **benefit from or require AI/LLMs** (e.g., semantic similarity, free-text linking, conflict explanation).

7. **Provide an incremental rollout plan**  
   - Phase 1: Minimal viable system (mostly deterministic, with limited AI).  
   - Phase 2: Introduce AI for semantic/soft-link tasks.  
   - Phase 3: Optimize performance and reliability, add active learning / feedback loops.

### Supporting Analysis (Input to the Design)

To support the design above, you should still perform targeted analysis of the datasets, focusing on what is necessary to drive the solution:

1. **Schema Heterogeneity Inventory**  
   - Complete mapping of field name variations per concept.

2. **Value Format Catalog**  
   - All important format variations with proposed normalization rules.

3. **Relationship Graph**  
   - Clear representation of how datasets connect (hard and soft links).

4. **Query Routing Patterns**  
   - How different query types map to concepts and sources.

5. **Data Map Requirements**  
   - What the data map must encode to support the desired behavior.

6. **Orchestration Challenges**  
   - Technical challenges and possible solution options (AI and non-AI).

7. **Implementation Recommendations**  
   - Concrete suggestions on technologies, patterns, and components to implement the engine.

### Key Constraints

- **No pre-transformation**: Do not recommend reshaping entire datasets
- **Dynamic routing**: Solutions must work at query time
- **On-demand normalization**: Normalize only what's needed for the query
- **Entity resolution**: Must handle ID variations and semantic matching
- **Scalability**: Solutions must work with 2000+ rows per dataset
- **Security** : Due to security we cant give all the data to the LLM

### Success Criteria

Your design and analysis should enable someone to:
- Understand exactly where each piece of information lives
- Know how to route any natural language query to the right data sources
- Understand how to normalize values on-the-fly
- Know how to resolve entities across heterogeneous sources
- Design a data map that supports dynamic query routing

---

## Part 9: Critical Understanding Points

### 9.1 Same Entity, Multiple Representations

**Clients:**
- One real-world client (e.g., Stonebridge Motors Inc) appears in 4 files
- Same `CL-1001` value but in fields: `client_id`, `id`, `cid`, `cust_code`
- Same company name but variations: `"Stonebridge Motors Inc"`, `"STONEBRIDGE MOTORS INC"`, `"Stonebridge Motors Company"`

**Matters:**
- One real-world matter (e.g., Master Services Agreement Negotiation) appears in 2 files
- Same `MAT-1011` value but in fields: `matter_id`, `file_no`
- May also appear as `MTR-1010` in billing file headers (intentional noise)

### 9.2 Value Equivalence

**Revenue:**
- `"$12,000,000"` (CSV string with currency symbols)
- `12000000` (JSON integer)
- `"12000000"` (XML string)
- All represent the same value: 12 million dollars

**Dates:**
- `"2022-09-25"` (ISO format)
- `"25/09/22"` (DD/MM/YY)
- `"1650844800"` (Unix timestamp)
- All represent the same date: September 25, 2022

### 9.3 Semantic Equivalence

**Client Names:**
- `"Stonebridge Motors Inc"` (structured, canonical)
- `"STONEBRIDGE MOTORS INC"` (uppercase variant)
- `"Stonebridge Motors Company"` (narrative, semantic variant)
- All refer to the same entity but require semantic matching

**Matter Titles:**
- `"Master Services Agreement Negotiation"` (structured)
- `"framework commercial arrangement Negotiation"` (narrative, semantic variant)
- Same meaning, different wording - requires embedding/LLM matching

### 9.4 Relationship Complexity

**Direct Relationships:**
- Matter → Client: Hard FK (`client_ref`/`client_id` → `client_id`/`id`/`cid`/`cust_code`)
- Billing → Matter: Hard FK (`file_id` → `matter_id`/`file_no`)
- Document → Matter: Hard FK (`matter_id` → `matter_id`/`file_no`)

**Indirect Relationships:**
- Email → Matter: Soft link via text analysis
- Regulation → Matter: Soft link via text search
- Billing File → Matter: Filename match, but header may have noisy alias


