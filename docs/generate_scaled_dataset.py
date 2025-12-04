#!/usr/bin/env python3
"""
Scalable dataset generator using Ollama gemma3:1b for text generation
Generates 2000+ rows per dataset with intentional inconsistencies
"""

import csv
import json
import random
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import requests
import time
from openpyxl import Workbook
from openpyxl.styles import Font

# Configuration
BASE_DIR = "/Users/mac/Desktop/work/legal-fusion"
PACK_DIR = os.path.join(BASE_DIR, "synthetic_heterogeneous_pack_scaled")
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:1b"  # Using gemma3:1b which is available

# Target counts
TARGET_CLIENTS = 2000
TARGET_MATTERS = 2000
TARGET_BILLING_ENTRIES = 2000
TARGET_DOCUMENTS = 2000

random.seed(42)

# Industry and practice area pools
INDUSTRIES = [
    "Automotive", "Healthcare", "Finance", "Retail", "Technology",
    "Manufacturing", "Energy", "Real Estate", "Telecommunications", "Aerospace",
    "Pharmaceuticals", "Banking", "Insurance", "Construction", "Transportation"
]

PRACTICE_AREAS = [
    "IP", "Employment", "Contracts", "Regulatory", "M&A",
    "Litigation", "Corporate", "Tax", "Immigration", "Environmental"
]

ATTORNEYS = [
    "Daniel Park", "Mark Thompson", "Hannah Lee", "Ayesha Khan", "Lina Gomez",
    "James Wilson", "Sarah Chen", "Michael Brown", "Emily Davis", "Robert Taylor"
]

DOC_TYPES = ["Contract", "Agreement", "Motion", "Brief", "Correspondence"]
FILE_TYPES = ["pdf", "docx", "txt"]


def call_ollama(prompt: str, max_retries: int = 3) -> str:
    """Call Ollama API for text generation"""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                print(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    # Fallback to template-based generation
    return generate_fallback_text(prompt)


def generate_fallback_text(prompt: str) -> str:
    """Fallback text generation if Ollama fails"""
    if "company name" in prompt.lower():
        templates = [
            "{industry} Solutions Inc", "{industry} Group LLC",
            "{industry} Holdings Corp", "{industry} Partners",
            "{industry} International", "{industry} Systems"
        ]
        industry = random.choice(INDUSTRIES)
        return random.choice(templates).format(industry=industry)
    elif "matter title" in prompt.lower():
        templates = [
            "{client} - Master Services Agreement",
            "{client} - Regulatory Inquiry",
            "{client} v. ACME Corp - Employment Dispute",
            "{client} - Contract Breach"
        ]
        return random.choice(templates)
    return "Generated content"


def generate_company_name(industry: str, use_llm: bool = True) -> Tuple[str, str]:
    """Generate company name with variations"""
    if use_llm:
        prompt = f"Generate a realistic company name in the {industry} industry. Return only the company name, nothing else."
        name = call_ollama(prompt)
    else:
        name = generate_fallback_text(f"company name {industry}")
    
    # Create variations
    variations = [
        name,
        name.upper(),
        name.replace(" Inc", " Company"),
        name.replace(" LLC", " Holdings"),
        name.replace(" Solutions", " Systems"),
    ]
    
    return name, random.choice(variations)


def format_date_variant(date_obj: datetime) -> str:
    """Generate date in various formats"""
    formats = [
        lambda d: d.strftime("%Y-%m-%d"),  # 2022-09-25
        lambda d: d.strftime("%d/%m/%y"),   # 25/09/22
        lambda d: d.strftime("%d-%b-%Y"),  # 25-Oct-2021
        lambda d: str(int(d.timestamp())),  # Unix timestamp
        lambda d: d.strftime("%d/%m/%Y"),   # 25/09/2022
    ]
    return random.choice(formats)(date_obj)


def format_phone_variant() -> str:
    """Generate phone in various formats"""
    area = random.randint(200, 999)
    prefix = random.randint(200, 999)
    number = random.randint(1000, 9999)
    
    formats = [
        f"({area}) {prefix}-{number}",
        f"+1-{area}-{prefix}-{number}",
        f"{area}.{prefix}.{number}",
        f"{area}-{prefix}-{number}",
    ]
    return random.choice(formats)


def format_currency_variant(amount: float) -> str:
    """Generate currency in various formats"""
    formats = [
        f"${amount:,.2f}",           # $12,000,000.00
        f"${amount:,.0f}",           # $12,000,000
        f'"{amount:,.2f}"',          # "12000000.00"
        str(int(amount)),            # 12000000
        f"{amount:,.0f}",            # 12,000,000
        f"€{amount:,.0f}",           # €12,000,000
    ]
    return random.choice(formats)


def generate_clients(num_clients: int = TARGET_CLIENTS) -> List[Dict]:
    """Generate client records"""
    clients = []
    print(f"Generating {num_clients} clients...")
    
    for i in range(1, num_clients + 1):
        client_id = f"CL-{1000 + i}"
        industry = random.choice(INDUSTRIES)
        name, name_variant = generate_company_name(industry, use_llm=(i % 10 == 0))  # Use LLM every 10th
        
        revenue = random.randint(1_000_000, 100_000_000)
        created_date = datetime.now() - timedelta(days=random.randint(30, 3650))
        
        client = {
            "client_id": client_id,
            "id": client_id,
            "cid": client_id,
            "company_name": name,
            "custFullNm": name_variant.upper(),
            "nm": name,
            "industry": industry,
            "sector": industry.lower(),
            "cat": industry,
            "annual_revenue": format_currency_variant(revenue),
            "annual_turnover": str(revenue),
            "turnover": revenue,
            "contact_phone": format_phone_variant(),
            "phone": format_phone_variant(),
            "created_at": format_date_variant(created_date),
            "created": format_date_variant(created_date),
            "registered_on": format_date_variant(created_date),
        }
        clients.append(client)
        
        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{num_clients} clients")
    
    return clients


def generate_matters(clients: List[Dict], num_matters: int = TARGET_MATTERS) -> List[Dict]:
    """Generate matter records"""
    matters = []
    print(f"Generating {num_matters} matters...")
    
    # Distribute matters across clients
    matters_per_client = num_matters // len(clients)
    extra_matters = num_matters % len(clients)
    
    matter_counter = 1
    for client_idx, client in enumerate(clients):
        num_for_client = matters_per_client + (1 if client_idx < extra_matters else 0)
        
        for _ in range(num_for_client):
            matter_id = f"MAT-{1000 + matter_counter}"
            practice_area = random.choice(PRACTICE_AREAS)
            attorney = random.choice(ATTORNEYS)
            start_date = datetime.now() - timedelta(days=random.randint(1, 1825))
            
            # Generate matter title
            title_templates = [
                f"{client['company_name']} - Master Services Agreement Negotiation",
                f"{client['company_name']} - Regulatory Inquiry",
                f"{client['company_name']} v. ACME Corp - Employment Dispute",
                f"{client['company_name']} - Contract Breach",
            ]
            title = random.choice(title_templates)
            
            est_value = random.randint(5000, 50000)
            
            matter = {
                "matter_id": matter_id,
                "file_no": matter_id,
                "file_id": matter_id,
                "client_id": client["client_id"],
                "client_ref": client["client_id"],
                "matterSummary": title,
                "title": title,
                "area": practice_area,
                "practice_area": practice_area,
                "startDate": format_date_variant(start_date),
                "opened_on": format_date_variant(start_date),
                "owner": attorney,
                "lead_attorney": attorney,
                "estimated_value": random.choice([
                    str(est_value),
                    format_currency_variant(est_value),
                    f"{est_value // 1000}K",
                ]),
            }
            matters.append(matter)
            matter_counter += 1
    
    print(f"  Generated {len(matters)} matters")
    return matters


def generate_billing_entries(matters: List[Dict], num_entries: int = TARGET_BILLING_ENTRIES) -> List[Dict]:
    """Generate billing entry records"""
    entries = []
    print(f"Generating {num_entries} billing entries...")
    
    # Distribute entries across matters
    entries_per_matter = num_entries // len(matters)
    extra_entries = num_entries % len(matters)
    
    entry_counter = 1
    descriptions = [
        "Reviewed contract", "Drafted motion", "Prepared discovery", "Client call",
        "Document review", "Research", "Court appearance", "Negotiation"
    ]
    
    for matter_idx, matter in enumerate(matters):
        num_for_matter = entries_per_matter + (1 if matter_idx < extra_entries else 0)
        
        for _ in range(num_for_matter):
            entry_id = f"BL-{random.randint(100000, 999999)}"
            att_id = f"AT-{random.randint(1, 10):03d}"
            hours = round(random.uniform(0.5, 10.0), 1)
            rate = random.choice([250, 300, 375])
            amount = round(hours * rate, 2)
            description = random.choice(descriptions)
            entry_date = datetime.now() - timedelta(days=random.randint(1, 1825))
            
            entry = {
                "entry_id": entry_id,
                "file_id": matter["matter_id"],
                "att_id": att_id,
                "hours": str(hours),
                "rate": str(rate),
                "amount": random.choice([
                    str(amount),
                    format_currency_variant(amount),
                    "",  # Sometimes missing
                ]),
                "description": description,
                "entry_date": format_date_variant(entry_date),
            }
            entries.append(entry)
            entry_counter += 1
    
    print(f"  Generated {len(entries)} billing entries")
    return entries


def generate_documents(matters: List[Dict], num_docs: int = TARGET_DOCUMENTS) -> List[Dict]:
    """Generate document metadata"""
    documents = []
    print(f"Generating {num_docs} documents...")
    
    # Distribute documents across matters
    docs_per_matter = num_docs // len(matters)
    extra_docs = num_docs % len(matters)
    
    doc_counter = 1
    for matter_idx, matter in enumerate(matters):
        num_for_matter = docs_per_matter + (1 if matter_idx < extra_docs else 0)
        
        for _ in range(num_for_matter):
            doc_id = f"D-{2000 + doc_counter}"
            doc_type = random.choice(DOC_TYPES)
            file_type = random.choice(FILE_TYPES)
            created_date = datetime.now() - timedelta(days=random.randint(1, 1825))
            uploaded_by = random.choice(ATTORNEYS)
            
            doc = {
                "doc_id": doc_id,
                "matter_id": matter["matter_id"],
                "client": matter["client_id"],
                "doc_type": doc_type,
                "title": f"{doc_type} Document",
                "created": format_date_variant(created_date),
                "uploaded_by": uploaded_by,
                "file_type": file_type,
            }
            documents.append(doc)
            doc_counter += 1
    
    print(f"  Generated {len(documents)} documents")
    return documents


def write_clients_csv(clients: List[Dict], filepath: str):
    """Write clients to CSV format A"""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'client_id', 'company_name', 'industry', 'annual_revenue',
            'contact_phone', 'created_at'
        ])
        writer.writeheader()
        for client in clients:
            writer.writerow({
                'client_id': client['client_id'],
                'company_name': client['company_name'],
                'industry': client['industry'],
                'annual_revenue': client['annual_revenue'],
                'contact_phone': client['contact_phone'],
                'created_at': client['created_at'],
            })


def write_clients_json(clients: List[Dict], filepath: str):
    """Write clients to JSON format B"""
    json_clients = []
    for client in clients:
        json_clients.append({
            "id": client["id"],
            "custFullNm": client["custFullNm"],
            "sector": client["sector"],
            "financials": {
                "turnover": client["turnover"],
                "currency": "USD"
            },
            "phone": client["phone"],
            "meta": {
                "registered_on": client["registered_on"]
            }
        })
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_clients, f, indent=2, ensure_ascii=False)


def write_clients_xml(clients: List[Dict], filepath: str):
    """Write clients to XML format C"""
    root = ET.Element("Clients")
    for client in clients:
        entity = ET.SubElement(root, "Entity")
        entity.set("cid", client["cid"])
        ET.SubElement(entity, "nm").text = client["nm"]
        ET.SubElement(entity, "annual_turnover").text = client["annual_turnover"]
        ET.SubElement(entity, "cat").text = client["cat"]
        ET.SubElement(entity, "phone").text = client["phone"]
    
    tree = ET.ElementTree(root)
    tree.write(filepath, encoding='utf-8', xml_declaration=True)


def write_clients_xlsx(clients: List[Dict], filepath: str):
    """Write clients to XLSX format D"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Clients"
    
    # Headers
    headers = ['cust_code', 'clientName', 'industry', 'revenue', 'phone', 'created']
    ws.append(headers)
    
    # Style headers
    for cell in ws[1]:
        cell.font = Font(bold=True)
    
    # Data
    for client in clients:
        ws.append([
            client['client_id'],
            client['company_name'],
            client['industry'],
            client['annual_turnover'],
            client['phone'],
            client['created_at'],
        ])
    
    wb.save(filepath)


def write_matters_csv(matters: List[Dict], filepath: str):
    """Write matters to CSV format A"""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'matter_id', 'client_ref', 'title', 'practice_area',
            'opened_on', 'lead_attorney', 'estimated_value'
        ])
        writer.writeheader()
        for matter in matters:
            writer.writerow({
                'matter_id': matter['matter_id'],
                'client_ref': matter['client_ref'],
                'title': matter['title'],
                'practice_area': matter['practice_area'],
                'opened_on': matter['opened_on'],
                'lead_attorney': matter['lead_attorney'],
                'estimated_value': matter['estimated_value'],
            })


def write_matters_json(matters: List[Dict], filepath: str):
    """Write matters to JSON format B"""
    json_matters = []
    for matter in matters:
        json_matters.append({
            "file_no": matter["file_no"],
            "client_id": matter["client_id"],
            "matterSummary": matter["matterSummary"],
            "area": matter["area"],
            "startDate": matter["startDate"],
            "owner": matter["owner"],
        })
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_matters, f, indent=2, ensure_ascii=False)


def write_billing_csv(entries: List[Dict], filepath: str):
    """Write billing entries to CSV"""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'entry_id', 'file_id', 'att_id', 'hours', 'rate',
            'amount', 'description', 'entry_date'
        ])
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry)


def write_documents_json(documents: List[Dict], filepath: str):
    """Write document metadata to JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)


def main():
    """Main generation function"""
    print("="*60)
    print("SCALABLE HETEROGENEOUS DATASET GENERATOR")
    print("="*60)
    print(f"Target: {TARGET_CLIENTS} clients, {TARGET_MATTERS} matters,")
    print(f"        {TARGET_BILLING_ENTRIES} billing entries, {TARGET_DOCUMENTS} documents")
    print("="*60)
    
    # Create output directory
    os.makedirs(PACK_DIR, exist_ok=True)
    os.makedirs(os.path.join(PACK_DIR, "documents"), exist_ok=True)
    os.makedirs(os.path.join(PACK_DIR, "documents", "filings"), exist_ok=True)
    os.makedirs(os.path.join(PACK_DIR, "regulations"), exist_ok=True)
    
    # Generate data
    clients = generate_clients(TARGET_CLIENTS)
    matters = generate_matters(clients, TARGET_MATTERS)
    billing_entries = generate_billing_entries(matters, TARGET_BILLING_ENTRIES)
    documents = generate_documents(matters, TARGET_DOCUMENTS)
    
    # Write structured clients (4 formats)
    print("\nWriting structured client files...")
    write_clients_csv(clients, os.path.join(PACK_DIR, "structured_clients_A.csv"))
    write_clients_json(clients, os.path.join(PACK_DIR, "structured_clients_B.json"))
    write_clients_xml(clients, os.path.join(PACK_DIR, "structured_clients_C.xml"))
    write_clients_xlsx(clients, os.path.join(PACK_DIR, "structured_clients_D.xlsx"))
    
    # Write matters (2 formats)
    print("Writing matter files...")
    write_matters_csv(matters, os.path.join(PACK_DIR, "matters_A.csv"))
    write_matters_json(matters, os.path.join(PACK_DIR, "matters_B.json"))
    
    # Write billing entries
    print("Writing billing entries...")
    write_billing_csv(billing_entries, os.path.join(PACK_DIR, "billing_entries_A.csv"))
    
    # Write document metadata
    print("Writing document metadata...")
    write_documents_json(documents, os.path.join(PACK_DIR, "document_metadata.json"))
    
    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"Generated {len(clients)} clients")
    print(f"Generated {len(matters)} matters")
    print(f"Generated {len(billing_entries)} billing entries")
    print(f"Generated {len(documents)} documents")
    print(f"\nOutput directory: {PACK_DIR}")


if __name__ == "__main__":
    main()

