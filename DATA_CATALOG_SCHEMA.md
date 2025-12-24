# Data Catalog Structure: `consolidated_descriptions.json`

This document explains the schema and purpose of the `consolidated_descriptions.json` file. This file acts as a **Semantic Data Catalog**, providing a unified, searchable, and machine-readable overview of all data assets within the `legal-fusion` ecosystem.

---

## 1. Root Structure
The JSON root contains two primary keys:
- `metadata`: Global execution statistics.
- `datasets`: An array of individual file analyses.

```json
{
  "metadata": { ... },
  "datasets": [ ... ]
}
```

---

## 2. Global Metadata (`metadata`)
Summarizes the state of the data ingestion process.

| Field | Description |
| :--- | :--- |
| `generated_at` | Timestamp of when the catalog was created. |
| `total_files` | Total number of supported files discovered in the data directory. |
| `success_count` | Number of files successfully analyzed by the LLM. |
| `failure_count` | Number of files that encountered errors during processing. |
| `duration_seconds` | The total wall-clock time taken for the run. |

---

## 3. Dataset Entry (`datasets[]`)
Each object in the `datasets` list represents a unique file.

### A. File Identification
- **`filename`**: The base name of the file (e.g., `billing_entries.csv`).
- **`file_path`**: The absolute system path to the file.
- **`relative_path`**: The path relative to the project root (used for portability).
- **`processed_at`**: Individual timestamp for when this file was indexed.

### B. Semantic Context (`file`)
Contains the high-level meaning extracted by the AI.
- **`name`**: A "Clean" human-readable name (e.g., "Matter Billing Records").
- **`description`**: A detailed summary of the file's content, legal context, and business relevance.
    - *Note: For `.txt` files, this is left empty as they are recorded but not analyzed by the LLM.*

### C. Column/Schema Definitions (`columns[]`)
A detailed map of the internal structure of the file.

| Field | Description |
| :--- | :--- |
| `name` | The raw column header or JSON key. |
| `description` | Semantic meaning of the field (e.g., "Unique ID for the billing cycle"). |
| `example` | A real-world sample value taken from the data. |
| `data_type` | Inferred technical type (`str`, `int`, `float`, `date`, etc.). |
| `similar_keywords` | A list of synonyms or related industry terms. **Used for automated data mapping and entity resolution.** |

---

## 4. Key Values & Benefits
1. **Searchability**: Allows for instant searching across the entire data lake without opening individual files.
2. **AI-Ready**: Provides the "Ground Truth" schema that LLMs need to write SQL queries or perform data transformations.
3. **Entity Resolution**: The `similar_keywords` field allows the system to realize that `matter_id` in one file is the same as `case_ref` in another, enabling automated data joining.
