#!/usr/bin/env python3
"""
Generate text documents using Ollama gemma3:1b
Creates billing narratives, document content, and other text files
"""

import json
import os
import random
import requests
import time
from typing import Dict, List
from datetime import datetime, timedelta

# Configuration
BASE_DIR = "/Users/mac/Desktop/work/legal-fusion"
PACK_DIR = os.path.join(BASE_DIR, "synthetic_heterogeneous_pack_scaled")
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:1b"  # Using gemma3:1b which is available

random.seed(42)


def call_ollama(prompt: str, max_retries: int = 3) -> str:
    """Call Ollama API for text generation"""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=120)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                print(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    
    # Fallback
    return generate_fallback_text(prompt)


def generate_fallback_text(prompt: str) -> str:
    """Fallback text generation"""
    if "billing summary" in prompt.lower():
        return """Billing Summary for Matter

This document contains billing entries for legal services rendered.
The matter involves various legal activities including contract review,
document preparation, and client consultations."""
    elif "contract" in prompt.lower():
        return """This is a legal contract document outlining the terms and conditions
of the agreement between parties. The document contains standard legal language
and provisions typical of commercial agreements."""
    return "Generated legal document content."


def generate_billing_narrative(matter: Dict, client: Dict, entries: List[Dict], is_noisy: bool = False) -> str:
    """Generate billing narrative text using LLM"""
    prompt = f"""Generate a brief billing summary narrative (2-3 sentences) for:
- Matter: {matter.get('title', 'Legal Matter')}
- Client: {client.get('company_name', 'Client')}
- Industry: {client.get('industry', 'General')}
- Number of entries: {len(entries)}

Write a professional legal billing narrative that summarizes the work performed."""
    
    if is_noisy:
        prompt += " Include some inconsistencies in terminology and references."
    
    narrative = call_ollama(prompt)
    
    # Add structured information
    lines = [
        f"Billing Summary for Matter {matter.get('matter_id', 'UNKNOWN')}",
        f"Simulated_Format: {random.choice(['PDF', 'DOCX', 'TXT'])}",
        "",
        f"matter_id: {matter.get('matter_id', 'UNKNOWN')}",
        f"ClientId: {client.get('client_id', 'UNKNOWN')}",
        "",
        "[Client Information]",
        f"client_name: {client.get('company_name', 'Unknown')}",
        f"Canonical client_id: {client.get('client_id', 'UNKNOWN')}",
        f"Canonical Client Name: {client.get('company_name', 'Unknown')}",
        f"industry: {client.get('industry', 'Unknown')}",
        "",
        "[Matter Information]",
        f"Case Title (narrative): {matter.get('title', 'Unknown Matter')}",
        f"Formal Matter Title: {matter.get('title', 'Unknown Matter')}",
        f"Practice Area: {matter.get('practice_area', 'Unknown')}",
        f"Lead Counsel: {matter.get('lead_attorney', 'Unknown')}",
        "",
        "[Billing Entries]",
    ]
    
    # Add sample entries
    for entry in entries[:5]:  # Limit to 5 entries per narrative
        lines.extend([
            f"- Entry ID: {entry.get('entry_id', 'UNKNOWN')}",
            f"  Attorney ID: {entry.get('att_id', 'UNKNOWN')}",
            f"  Hours Billed: {entry.get('hours', '0')}",
            f"  Hourly Rate: {entry.get('rate', '0')}",
            f"  Amount: {entry.get('amount', '0')}",
            f"  Work Description: {entry.get('description', 'Legal work')}",
            f"  Entry Date (raw): {entry.get('entry_date', 'Unknown')}",
            "",
        ])
    
    lines.extend([
        "[Narrative Summary]",
        narrative,
        ""
    ])
    
    return "\n".join(lines)


def generate_document_content(doc: Dict, matter: Dict, client: Dict) -> str:
    """Generate document content using LLM"""
    doc_type = doc.get('doc_type', 'Document')
    prompt = f"""Generate a short legal {doc_type.lower()} document (3-4 paragraphs) for:
- Client: {client.get('company_name', 'Client')}
- Matter: {matter.get('title', 'Legal Matter')}
- Document Type: {doc_type}

Write realistic legal document content with appropriate legal language."""
    
    content = call_ollama(prompt)
    
    # Add metadata header
    header = f"""Document ID: {doc.get('doc_id', 'UNKNOWN')}
Matter ID: {doc.get('matter_id', 'UNKNOWN')}
Client: {doc.get('client', 'UNKNOWN')}
Document Type: {doc.get('doc_type', 'Unknown')}
Created: {doc.get('created', 'Unknown')}
Uploaded By: {doc.get('uploaded_by', 'Unknown')}

---

"""
    
    return header + content


def generate_filing_content(filing_id: str, matter: Dict) -> str:
    """Generate filing document content"""
    prompt = f"""Generate a short court filing document (2-3 paragraphs) for matter:
{matter.get('title', 'Legal Matter')}

Write realistic court filing content with appropriate legal language."""
    
    content = call_ollama(prompt)
    
    header = f"""Filing ID: {filing_id}
Matter: {matter.get('matter_id', 'UNKNOWN')}
Date: {datetime.now().strftime('%Y-%m-%d')}

---

"""
    
    return header + content


def main():
    """Generate all text documents"""
    print("="*60)
    print("TEXT DOCUMENT GENERATOR (Ollama)")
    print("="*60)
    
    # Load generated data
    print("Loading generated data...")
    with open(os.path.join(PACK_DIR, "document_metadata.json"), 'r') as f:
        documents = json.load(f)
    
    with open(os.path.join(PACK_DIR, "matters_A.csv"), 'r') as f:
        import csv
        matters = list(csv.DictReader(f))
    
    with open(os.path.join(PACK_DIR, "structured_clients_A.csv"), 'r') as f:
        clients = list(csv.DictReader(f))
    
    with open(os.path.join(PACK_DIR, "billing_entries_A.csv"), 'r') as f:
        billing_entries = list(csv.DictReader(f))
    
    # Create lookup dictionaries
    matters_by_id = {m['matter_id']: m for m in matters}
    clients_by_id = {c['client_id']: c for c in clients}
    billing_by_matter = {}
    for entry in billing_entries:
        matter_id = entry.get('file_id')
        if matter_id:
            billing_by_matter.setdefault(matter_id, []).append(entry)
    
    # Generate document files
    print(f"\nGenerating {len(documents)} document files...")
    for i, doc in enumerate(documents):
        matter_id = doc.get('matter_id')
        client_id = doc.get('client')
        matter = matters_by_id.get(matter_id, {})
        client = clients_by_id.get(client_id, {})
        
        content = generate_document_content(doc, matter, client)
        
        file_type = doc.get('file_type', 'txt')
        filename = f"{doc.get('doc_id', f'D-{i}')}_{file_type}.txt"
        filepath = os.path.join(PACK_DIR, "documents", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{len(documents)} documents")
    
    # Generate billing narratives
    print(f"\nGenerating billing narratives...")
    os.makedirs(os.path.join(BASE_DIR, "billing_files_scaled"), exist_ok=True)
    
    unique_matters = list(set(m.get('matter_id') for m in matters))
    for i, matter_id in enumerate(unique_matters[:2000]):  # Limit to 2000
        matter = matters_by_id.get(matter_id, {})
        client_id = matter.get('client_ref')
        client = clients_by_id.get(client_id, {})
        entries = billing_by_matter.get(matter_id, [])
        
        is_noisy = (i % 2 == 0)  # Every other one is noisy
        narrative = generate_billing_narrative(matter, client, entries, is_noisy)
        
        filepath = os.path.join(BASE_DIR, "billing_files_scaled", f"{matter_id}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(narrative)
        
        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1} billing narratives")
    
    print("\n" + "="*60)
    print("TEXT GENERATION COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()

