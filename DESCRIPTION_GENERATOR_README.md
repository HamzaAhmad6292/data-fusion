# Description Generator Documentation

## Overview

The `DescriptionGenerator` (`app/description_generator.py`) is an intelligent tool designed to automatically generate comprehensive documentation for datasets. It combines programmatic data analysis with LLM capabilities to produce detailed file-level and column-level descriptions.

## Core Capabilities

1.  **Multi-Format Support**: Handles CSV, Excel (`.xlsx`, `.xls`), JSON, JSONL, and Text files.
2.  **Hybrid Analysis**:
    *   **Programmatic Analysis**: Infers precise data types (int, float, bool, datetime, etc.) by analyzing the actual data.
    *   **Semantic Analysis**: Uses an LLM to understand the *meaning* of the data, generating human-readable descriptions and identifying synonyms.
3.  **Robust Error Handling**: Includes retry logic for LLM rate limits and intelligent JSON parsing to handle various LLM response formats.

## How It Works

### 1. Data Sampling & Type Inference
*   **Sampling**: The system extracts a representative sample (top 5 rows/records) from the dataset using format-specific processors.
*   **Type Inference**:
    *   For tabular data (CSV/Excel), it scans the full column to determine the pandas `dtype`.
    *   For semi-structured data (JSON/JSONL), it samples records to find the most common non-null data type for each field.

### 2. LLM Prompting Strategy
The system uses a sophisticated prompting strategy to ensure high-quality output:
*   **Persona**: Acts as an "experienced data engineer".
*   **Input**: Receives the raw data sample.
*   **Output Constraint**: Strictly enforced JSON format containing:
    *   `file`: Overall dataset name and description.
    *   `columns`: Array of column details (name, description, example, similar keywords).

### 3. Response Processing
*   **Extraction**: Robust regex patterns extract valid JSON from the LLM's response, handling cases where the LLM wraps output in Markdown code blocks.
*   **Enrichment**: The semantic descriptions from the LLM are merged with the programmatically inferred data types to create a complete profile for each column.

## Output Structure

The tool outputs a JSON object with the following structure:

```json
{
  "filename": "dataset.csv",
  "file_path": "/path/to/dataset.csv",
  "file": {
    "name": "Human-readable Dataset Name",
    "description": "High-level description of the dataset's purpose and domain."
  },
  "columns": [
    {
      "name": "column_name",
      "description": "Semantic description of what this column represents.",
      "example": "Actual value from data",
      "similar_keywords": ["synonym1", "synonym2"],
      "data_type": "int" 
    }
  ]
}
```

## Usage

### As a Library
```python
from app.description_generator import generate_description

# Generate descriptions and return as dict
result = generate_description("path/to/data.csv")

# Generate and save to file
generate_description("path/to/data.csv", output_path="path/to/output.json")
```

### via Command Line
```bash
python app/description_generator.py <input_file_path> [output_file_path]
```

## Consolidated Description Service

The `DescriptionService` (`services/description_service.py`) is a higher-level utility that crawls the entire `data/` directory, processes all supported files, and consolidates the results into a single master JSON file.

### Features
*   **Recursive Discovery**: Automatically finds all CSV, JSON, JSONL, and XLSX files.
*   **Rich UI**: Provides a beautiful CLI interface with progress bars, status tables, and detailed logging.
*   **Consolidation**: Merges all descriptions into `data/consolidated_descriptions.json`.
*   **Smart Skipping**: Automatically bypasses `.txt` files (only records path/name) and previous result files.

### Usage
```bash
# Run for all files in the data directory
python services/description_service.py

# Specify a custom data directory and output file
python services/description_service.py --data-dir path/to/data --output results.json

# Limit processing to first N files (useful for testing)
python services/description_service.py --limit 5
```
