# Scaled Dataset Generation Guide

## Overview

This system generates 2000+ rows per dataset with intentional inconsistencies, using Ollama's gemma2:1b (or gemma3:1b) for text generation.

## Prerequisites

1. **Ollama installed and running**
   ```bash
   # Install Ollama (if not already installed)
   # Visit: https://ollama.ai
   
   # Pull the model
   ollama pull gemma2:1b
   # OR
   ollama pull gemma3:1b
   
   # Verify Ollama is running
   curl http://localhost:11434/api/tags
   ```

2. **Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Generation Process

### Step 1: Generate Structured Data

This creates CSV, JSON, XML, and XLSX files with 2000+ rows each:

```bash
python generate_scaled_dataset.py
```

**Output:**
- `synthetic_heterogeneous_pack_scaled/structured_clients_A.csv` (2000 rows)
- `synthetic_heterogeneous_pack_scaled/structured_clients_B.json` (2000 rows)
- `synthetic_heterogeneous_pack_scaled/structured_clients_C.xml` (2000 rows)
- `synthetic_heterogeneous_pack_scaled/structured_clients_D.xlsx` (2000 rows)
- `synthetic_heterogeneous_pack_scaled/matters_A.csv` (2000 rows)
- `synthetic_heterogeneous_pack_scaled/matters_B.json` (2000 rows)
- `synthetic_heterogeneous_pack_scaled/billing_entries_A.csv` (2000 rows)
- `synthetic_heterogeneous_pack_scaled/document_metadata.json` (2000 entries)

### Step 2: Generate Text Documents (LLM-based)

This uses Ollama to generate text content for documents and billing narratives:

```bash
python generate_text_documents.py
```

**Output:**
- `synthetic_heterogeneous_pack_scaled/documents/*.txt` (2000 document files)
- `billing_files_scaled/*.txt` (2000 billing narrative files)

## Features

### Intentional Inconsistencies

1. **Schema Variations**
   - Client ID: `client_id`, `id`, `cid`, `client`
   - Client Name: `company_name`, `custFullNm`, `nm`
   - Revenue: `annual_revenue`, `annual_turnover`, `financials.turnover`

2. **Value Format Variations**
   - Dates: `2022-09-25`, `25/09/22`, `25-Oct-2021`, Unix timestamps
   - Phone: `(555) 125-5506`, `+1-555-338-9279`, `555.489.2584`
   - Currency: `$12,000,000`, `12000000`, `"$1,675.00"`, `€12,000`

3. **Name Variations**
   - Same entity: "Stonebridge Motors Inc" vs "STONEBRIDGE MOTORS INC" vs "Stonebridge Motors Company"

4. **ID Variations**
   - Matter IDs: `MAT-1011` vs `MTR-1010`

### Data Relationships

- **Clients** → **Matters** (1:many)
- **Matters** → **Billing Entries** (1:many)
- **Matters** → **Documents** (1:many)
- All entities maintain referential integrity despite format variations

## Configuration

Edit the constants in `generate_scaled_dataset.py`:

```python
TARGET_CLIENTS = 2000
TARGET_MATTERS = 2000
TARGET_BILLING_ENTRIES = 2000
TARGET_DOCUMENTS = 2000
OLLAMA_MODEL = "gemma2:1b"  # or "gemma3:1b"
```

## Performance Notes

- **Structured data generation**: ~5-10 minutes for 2000 rows each
- **Text generation**: ~30-60 minutes (depends on Ollama performance)
- LLM calls are made every 10th client for name generation (to balance quality/speed)
- Fallback templates used if Ollama is unavailable

## Troubleshooting

### Ollama not responding
- Check if Ollama is running: `curl http://localhost:11434/api/tags`
- Start Ollama: `ollama serve`
- The script will use fallback templates if Ollama fails

### Memory issues
- Reduce batch sizes in the scripts
- Generate in smaller chunks
- Use a smaller model if available

### Slow generation
- Reduce LLM usage frequency (change `use_llm=(i % 10 == 0)` to `(i % 50 == 0)`)
- Use fallback templates only (set `use_llm=False`)

## Output Structure

```
synthetic_heterogeneous_pack_scaled/
├── structured_clients_A.csv
├── structured_clients_B.json
├── structured_clients_C.xml
├── structured_clients_D.xlsx
├── matters_A.csv
├── matters_B.json
├── billing_entries_A.csv
├── document_metadata.json
└── documents/
    ├── D-2000_pdf.txt
    ├── D-2001_txt.txt
    └── ...

billing_files_scaled/
├── MAT-1001.txt
├── MAT-1002.txt
└── ...
```

## Next Steps

After generation, you can:
1. Analyze the data using `analyze_mismatches.py`
2. Generate reliability reports
3. Test entity resolution algorithms
4. Validate schema matching systems


