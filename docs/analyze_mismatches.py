#!/usr/bin/env python3
"""
Analyze mismatched concepts/terms across the heterogeneous dataset
"""

import json
import csv
import xml.etree.ElementTree as ET
from collections import defaultdict
import re

# Track mismatches
schema_mismatches = defaultdict(set)  # concept -> set of field names
value_mismatches = defaultdict(set)   # entity -> set of value representations
id_mismatches = defaultdict(set)      # entity -> set of IDs
date_format_mismatches = set()
phone_format_mismatches = set()
currency_format_mismatches = set()
name_variations = defaultdict(set)    # canonical name -> variations

# Analyze structured_clients_A.csv
print("Analyzing structured_clients_A.csv...")
with open('synthetic_heterogeneous_pack/structured_clients_A.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        client_id = row['client_id']
        name_variations[client_id].add(row['company_name'])
        schema_mismatches['client_identifier'].add('client_id')
        schema_mismatches['client_name'].add('company_name')
        schema_mismatches['industry'].add('industry')
        schema_mismatches['revenue'].add('annual_revenue')
        schema_mismatches['phone'].add('contact_phone')
        schema_mismatches['date'].add('created_at')
        
        # Value format tracking
        if row['annual_revenue']:
            currency_format_mismatches.add(row['annual_revenue'])
        if row['contact_phone'] and row['contact_phone'] != 'N/A':
            phone_format_mismatches.add(row['contact_phone'])
        if row['created_at']:
            date_format_mismatches.add(row['created_at'])

# Analyze structured_clients_B.json
print("Analyzing structured_clients_B.json...")
with open('synthetic_heterogeneous_pack/structured_clients_B.json', 'r') as f:
    data = json.load(f)
    for client in data:
        client_id = client['id']
        name_variations[client_id].add(client['custFullNm'])
        schema_mismatches['client_identifier'].add('id')
        schema_mismatches['client_name'].add('custFullNm')
        schema_mismatches['industry'].add('sector')
        schema_mismatches['revenue'].add('financials.turnover')
        schema_mismatches['phone'].add('phone')
        schema_mismatches['date'].add('meta.registered_on')
        
        # Value format tracking
        if client.get('financials', {}).get('turnover'):
            currency_format_mismatches.add(str(client['financials']['turnover']))
        if client.get('phone'):
            phone_format_mismatches.add(client['phone'])
        if client.get('meta', {}).get('registered_on'):
            date_format_mismatches.add(client['meta']['registered_on'])

# Analyze structured_clients_C.xml
print("Analyzing structured_clients_C.xml...")
tree = ET.parse('synthetic_heterogeneous_pack/structured_clients_C.xml')
root = tree.getroot()
for entity in root.findall('Entity'):
    client_id = entity.get('cid')
    name = entity.find('nm').text
    name_variations[client_id].add(name)
    schema_mismatches['client_identifier'].add('cid')
    schema_mismatches['client_name'].add('nm')
    schema_mismatches['industry'].add('cat')
    schema_mismatches['revenue'].add('annual_turnover')
    schema_mismatches['phone'].add('phone')
    
    # Value format tracking
    if entity.find('annual_turnover') is not None:
        currency_format_mismatches.add(entity.find('annual_turnover').text)
    if entity.find('phone') is not None:
        phone_format_mismatches.add(entity.find('phone').text)

# Analyze matters_B.json
print("Analyzing matters_B.json...")
with open('synthetic_heterogeneous_pack/matters_B.json', 'r') as f:
    matters = json.load(f)
    for matter in matters:
        schema_mismatches['matter_identifier'].add('file_no')
        schema_mismatches['client_identifier'].add('client_id')
        schema_mismatches['matter_description'].add('matterSummary')
        schema_mismatches['practice_area'].add('area')
        schema_mismatches['date'].add('startDate')
        schema_mismatches['attorney'].add('owner')
        
        if matter.get('startDate'):
            date_format_mismatches.add(str(matter['startDate']))

# Analyze billing_entries_A.csv
print("Analyzing billing_entries_A.csv...")
with open('synthetic_heterogeneous_pack/billing_entries_A.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        schema_mismatches['billing_identifier'].add('entry_id')
        schema_mismatches['matter_identifier'].add('file_id')
        schema_mismatches['attorney_identifier'].add('att_id')
        schema_mismatches['amount'].add('amount')
        schema_mismatches['date'].add('entry_date')
        
        # Value format tracking
        if row['amount']:
            currency_format_mismatches.add(row['amount'])
        if row['entry_date']:
            date_format_mismatches.add(row['entry_date'])

# Analyze document_metadata.json
print("Analyzing document_metadata.json...")
with open('synthetic_heterogeneous_pack/document_metadata.json', 'r') as f:
    docs = json.load(f)
    for doc in docs:
        schema_mismatches['document_identifier'].add('doc_id')
        schema_mismatches['matter_identifier'].add('matter_id')
        schema_mismatches['client_identifier'].add('client')
        schema_mismatches['date'].add('created')
        
        if doc.get('created'):
            date_format_mismatches.add(str(doc['created']))

# Check billing files for name variations
print("Analyzing billing files...")
import os
billing_dir = 'billing_files'
if os.path.exists(billing_dir):
    for filename in os.listdir(billing_dir):
        if filename.endswith('.txt'):
            with open(os.path.join(billing_dir, filename), 'r') as f:
                content = f.read()
                # Extract client name variations
                client_name_match = re.search(r'client_name:\s*(.+)', content, re.IGNORECASE)
                canonical_match = re.search(r'Canonical Client Name:\s*(.+)', content, re.IGNORECASE)
                if client_name_match and canonical_match:
                    name_variations['variation'].add(client_name_match.group(1).strip())
                    name_variations['variation'].add(canonical_match.group(1).strip())
                
                # Check for matter ID variations
                matter_id_match = re.search(r'matter_id:\s*(.+)', content, re.IGNORECASE)
                if matter_id_match:
                    matter_id = matter_id_match.group(1).strip()
                    # Check if it differs from MAT- format
                    if not matter_id.startswith('MAT-'):
                        id_mismatches['matter'].add(matter_id)

# Count unique mismatches
print("\n" + "="*60)
print("MISMATCH ANALYSIS RESULTS")
print("="*60)

# Schema mismatches (concepts with different field names)
print(f"\n1. SCHEMA MISMATCHES (Concepts with different field names):")
total_schema_mismatches = 0
for concept, field_names in schema_mismatches.items():
    if len(field_names) > 1:
        count = len(field_names)
        total_schema_mismatches += count
        print(f"   {concept}: {count} variations - {', '.join(sorted(field_names))}")

print(f"\n   Total Schema Mismatches: {total_schema_mismatches} field name variations")

# Value format mismatches
print(f"\n2. VALUE FORMAT MISMATCHES:")
print(f"   Date Formats: {len(date_format_mismatches)} unique formats")
print(f"   Phone Formats: {len(phone_format_mismatches)} unique formats")
print(f"   Currency/Numeric Formats: {len(currency_format_mismatches)} unique formats")
total_value_mismatches = len(date_format_mismatches) + len(phone_format_mismatches) + len(currency_format_mismatches)
print(f"\n   Total Value Format Mismatches: {total_value_mismatches}")

# Name variations
print(f"\n3. NAME VARIATIONS (Same entity, different representations):")
total_name_variations = 0
for entity_id, names in name_variations.items():
    if len(names) > 1:
        count = len(names)
        total_name_variations += count
        print(f"   {entity_id}: {count} variations - {', '.join(sorted(names))}")

print(f"\n   Total Name Variations: {total_name_variations}")

# ID mismatches
print(f"\n4. ID MISMATCHES (Same entity, different IDs):")
total_id_mismatches = 0
for entity_type, ids in id_mismatches.items():
    if len(ids) > 1:
        count = len(ids)
        total_id_mismatches += count
        print(f"   {entity_type}: {count} ID variations - {', '.join(sorted(ids))}")

print(f"\n   Total ID Mismatches: {total_id_mismatches}")

# Grand total
print("\n" + "="*60)
print("GRAND TOTAL MISMATCHES")
print("="*60)
grand_total = total_schema_mismatches + total_value_mismatches + total_name_variations + total_id_mismatches
print(f"Total Mismatched Concepts/Terms: {grand_total}")
print(f"\nBreakdown:")
print(f"  - Schema field name variations: {total_schema_mismatches}")
print(f"  - Value format variations: {total_value_mismatches}")
print(f"  - Name representation variations: {total_name_variations}")
print(f"  - ID variations: {total_id_mismatches}")



