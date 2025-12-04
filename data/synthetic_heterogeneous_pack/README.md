# Synthetic Heterogeneous Legal Dataset Pack

This dataset pack is intentionally heterogeneous to showcase schema matching, entity resolution, and data fusion.

Files and notable quirks:
- billing_entries_A.csv
- document_metadata.json
- documents/D-2000_pdf.txt
- documents/D-2001_txt.txt
- documents/D-2002_pdf.txt
- documents/D-2003_txt.txt
- documents/D-2004_txt.txt
- documents/D-2005_pdf.txt
- documents/D-2006_docx.txt
- documents/D-2007_docx.txt
- documents/D-2008_pdf.txt
- documents/D-2009_txt.txt
- documents/D-2010_txt.txt
- documents/D-2011_txt.txt
- documents/D-2012_txt.txt
- documents/D-2013_txt.txt
- documents/D-2014_docx.txt
- documents/D-2015_txt.txt
- documents/D-2016_pdf.txt
- documents/D-2017_txt.txt
- documents/D-2018_pdf.txt
- documents/D-2019_docx.txt
- documents/D-2020_pdf.txt
- documents/D-2021_docx.txt
- documents/D-2022_docx.txt
- documents/D-2023_txt.txt
- documents/D-2024_pdf.txt
- documents/D-2025_docx.txt
- documents/D-2026_txt.txt
- documents/D-2027_txt.txt
- documents/D-2028_docx.txt
- documents/D-2029_docx.txt
- documents/D-2030_txt.txt
- documents/D-2031_txt.txt
- documents/D-2032_docx.txt
- documents/D-2033_txt.txt
- documents/D-2034_pdf.txt
- documents/D-2035_txt.txt
- documents/D-2036_txt.txt
- documents/D-2037_txt.txt
- documents/D-2038_docx.txt
- documents/D-2039_pdf.txt
- documents/filings/AFF-0006.txt
- documents/filings/AFF-0009.txt
- documents/filings/AFF-0012.txt
- documents/filings/AFF-0014.txt
- documents/filings/AFF-0017.txt
- documents/filings/COM-0001.txt
- documents/filings/COM-0003.txt
- documents/filings/COM-0018.txt
- documents/filings/MTD-0002.txt
- documents/filings/MTD-0004.txt
- documents/filings/MTD-0005.txt
- documents/filings/MTD-0007.txt
- documents/filings/MTD-0008.txt
- documents/filings/MTD-0010.txt
- documents/filings/MTD-0011.txt
- documents/filings/MTD-0013.txt
- documents/filings/MTD-0015.txt
- documents/filings/MTD-0016.txt
- documents/filings/MTD-0019.txt
- documents/filings/MTD-0020.txt
- emails_A.jsonl
- matters_A.csv
- matters_B.json
- regulations/REG-300.txt
- regulations/REG-301.txt
- regulations/REG-302.txt
- regulations/REG-303.txt
- regulations/REG-304.txt
- regulations/REG-305.txt
- structured_clients_A.csv
- structured_clients_B.json
- structured_clients_C.xml
- structured_clients_D.xlsx

Heterogeneity features included:
- Multiple file formats: CSV, JSON, XML, XLSX, JSONL, TXT
- Schema-level variations (client_id vs custFullNm vs cid vs cust_code)
- Data-type variations for dates, currencies, and booleans
- Value-level spelling and abbreviation differences for the same canonical entities
- Semantically-equivalent yet lexically-different contract clauses to challenge embedding-based retrieval
- Intentional missing values and contradictory entries to force human-in-the-loop entity resolution

Reference: Demo flow uploaded by user is available at local path: /mnt/data/Demo_Flow_Explained.pdf