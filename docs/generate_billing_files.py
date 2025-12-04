import csv
import os
import random
from typing import Dict, List, Any, Optional

# Adjust these if your folder layout changes
BASE_DIR = "/Users/mac/Desktop/work/legal-fusion"
PACK_DIR = os.path.join(BASE_DIR, "synthetic_heterogeneous_pack")
OUTPUT_DIR = os.path.join(BASE_DIR, "billing_files")

random.seed(42)


def read_csv_dict(path: str) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_number(val: Optional[str]) -> Optional[float]:
    if val is None:
        return None
    s = val.strip()
    if not s:
        return None
    # Strip currency symbols, commas, letters; keep digits, dot, minus
    cleaned = "".join(ch for ch in s if (ch.isdigit() or ch in ".-"))
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def safe(val: Any, default: str = "") -> str:
    if val is None:
        return default
    s = str(val).strip()
    return s if s else default


def drift_client_name(name: str) -> str:
    # Lexical variants that keep rough meaning but differ a lot in wording
    if "Inc" in name:
        return name.replace("Inc", "Company")
    if "Group" in name:
        return name.replace("Group", "Consortium")
    if "LLC" in name:
        return name.replace("LLC", "Holdings")
    if "Solutions" in name:
        return name.replace("Solutions", "Systems")
    if "Motors" in name:
        return name.replace("Motors", "Automotive Works")
    return name + " International"


def drift_matter_title(title: str) -> str:
    out = title
    replacements = [
        ("Regulatory Inquiry", random.choice([
            "government agency probe",
            "oversight investigation",
            "regulatory oversight review",
        ])),
        ("Master Services Agreement", random.choice([
            "framework commercial arrangement",
            "long-term supply accord",
            "strategic services framework",
        ])),
        ("Employment Dispute", random.choice([
            "workforce conflict",
            "labor controversy",
            "staff relations dispute",
        ])),
        ("Contract Breach", random.choice([
            "agreement breakdown",
            "failure to honor obligations",
            "deal non‑performance",
        ])),
    ]
    for needle, repl in replacements:
        if needle in out:
            out = out.replace(needle, repl)
    return out


def variant_field_name(base: str) -> str:
    variants = {
        "client_id": ["client_ref", "cust_code", "Customer-ID", "ClientId"],
        "client_name": ["company_name", "Corporate Counterparty", "nm", "name_short"],
        "annual_revenue": ["annual_turnover", "turnover", "rev_k"],
        "matter_id": ["file_no", "MTR-ID", "Case Ref"],
        "opened_on": ["opened", "start_date", "init_date"],
    }
    if base not in variants:
        return base
    choices = [base] + variants[base]
    return random.choice(choices)


def choose_noisy_and_formats(file_ids: List[str]):
    file_ids_sorted = sorted(file_ids)
    n = len(file_ids_sorted)

    # About half noisy: for 15 matters -> 7 noisy, 8 clean
    num_noisy = n // 2  # 7 when n=15
    noisy_candidates = file_ids_sorted[::2]
    noisy_file_ids = set(noisy_candidates[:num_noisy])

    # Assign simulated formats: 5 PDF, 5 DOCX, 5 TXT
    format_map = {}
    for i, fid in enumerate(file_ids_sorted):
        if i < 5:
            fmt = "PDF"
        elif i < 10:
            fmt = "DOCX"
        else:
            fmt = "TXT"
        format_map[fid] = fmt

    return noisy_file_ids, format_map, file_ids_sorted


def build_content_for_matter(
    file_id: str,
    entries: List[Dict[str, str]],
    matter: Dict[str, str],
    client: Dict[str, str],
    is_noisy: bool,
    simulated_format: str,
    all_clients: Dict[str, Dict[str, str]],
    all_file_ids: List[str],
) -> str:
    # Canonical values
    real_matter_id = file_id
    real_client_id = matter.get("client_ref")
    real_client_name = client.get("company_name")

    # Maybe pick an alternative client for noisy header inconsistencies
    alt_client_id = real_client_id
    alt_client_name = real_client_name
    other_client_ids = [cid for cid in all_clients.keys() if cid != real_client_id]
    if is_noisy and other_client_ids:
        alt_client_id = random.choice(other_client_ids)
        alt_client_name = drift_client_name(all_clients[alt_client_id]["company_name"])

    # Maybe create a "wrong" matter alias for noisy files
    matter_alias = real_matter_id
    if is_noisy:
        # Use prefix MTR- and sometimes tweak the tail digits slightly
        numeric_part = real_matter_id.split("-")[-1]
        try:
            num = int(numeric_part)
            tweak = random.choice([-1, 0, 1])
            alias_num = max(1000, num + tweak)
            matter_alias = f"MTR-{alias_num}"
        except ValueError:
            matter_alias = "MTR-" + real_matter_id

    # Compute totals
    total_hours = 0.0
    total_amount = 0.0
    for e in entries:
        h = parse_number(e.get("hours"))
        if h is not None:
            total_hours += h
        a = parse_number(e.get("amount"))
        if a is not None:
            total_amount += a

    # For noisy files, fudge the displayed totals slightly
    if is_noisy:
        hours_display = round(total_hours * random.choice([0.95, 1.05, 1.1]), 2)
        amount_display = round(total_amount * random.choice([0.9, 1.0, 1.1]), 2)
    else:
        hours_display = round(total_hours, 2)
        amount_display = round(total_amount, 2)

    # Lexical drift for titles and names in noisy files
    matter_title_clean = matter.get("title", "")
    matter_title_noisy = drift_matter_title(matter_title_clean) if is_noisy else matter_title_clean

    client_name_clean = real_client_name
    client_name_noisy = drift_client_name(real_client_name) if is_noisy else real_client_name

    # Client & matter fields
    industry = client.get("industry")
    annual_revenue = client.get("annual_revenue")
    created_at = client.get("created_at")

    practice_area = matter.get("practice_area")
    opened_on = matter.get("opened_on")
    lead_attorney = matter.get("lead_attorney")
    est_value = matter.get("estimated_value")

    # Build text lines
    lines = []

    # Header
    lines.append(f"Billing Summary for Matter {real_matter_id}")
    lines.append(f"Simulated_Format: {simulated_format}")
    lines.append("")

    # Potentially inconsistent header IDs
    if is_noisy:
        lines.append(f"{variant_field_name('matter_id')}: {matter_alias}")
        lines.append(f"{variant_field_name('client_id')}: {alt_client_id}")
    else:
        lines.append(f"Matter ID: {real_matter_id}")
        lines.append(f"Client ID: {real_client_id}")
    lines.append("")

    # Client section (include both clean and noisy variants to create conflicts)
    lines.append("[Client Information]")
    if is_noisy:
        lines.append(f"{variant_field_name('client_name')}: {client_name_noisy}")
        lines.append(f"Canonical client_id: {real_client_id}")
        lines.append(f"Canonical Client Name: {client_name_clean}")
    else:
        lines.append(f"Client Name: {client_name_clean}")

    if industry:
        label = variant_field_name("industry") if is_noisy else "Industry"
        lines.append(f"{label}: {industry}")
    if annual_revenue:
        label = variant_field_name("annual_revenue") if is_noisy else "Annual Revenue"
        lines.append(f"{label}: {annual_revenue}")
    if created_at:
        lines.append(f"Client Created At: {created_at}")
    lines.append("")

    # Matter section
    lines.append("[Matter Information]")
    if is_noisy:
        lines.append(f"Case Title (narrative): {matter_title_noisy}")
        lines.append(f"Formal Matter Title: {matter_title_clean}")
    else:
        lines.append(f"Matter Title: {matter_title_clean}")

    if practice_area:
        lines.append(f"Practice Area: {practice_area}")
    if lead_attorney:
        # Introduce minor lexical drift in noisy files
        label = "Lead Counsel" if is_noisy else "Lead Attorney"
        lines.append(f"{label}: {lead_attorney}")
    if opened_on:
        label = variant_field_name("opened_on") if is_noisy else "Opened On"
        lines.append(f"{label}: {opened_on}")
    if est_value:
        lines.append(f"Estimated Value: {est_value}")
    lines.append("")

    # Random extra details for realism / noise
    if is_noisy:
        extra_notes = [
            "Internal Reference: SB-ENG-47 (not present in core systems).",
            "Phase 2 negotiations mentioned in board briefing memo.",
            "Parallel discussion with a separate regional subsidiary (not linked here).",
            "Legacy client code in archival system: LEG-" + real_client_id.split("-")[-1],
        ]
        lines.append("[Additional Context (Noisy / Partially Redundant)]")
        lines.append(random.choice(extra_notes))
        lines.append("")

    # Billing entries
    lines.append("[Billing Entries]")
    for e in entries:
        entry_id = e.get("entry_id")
        att_id = e.get("att_id")
        hours = e.get("hours")
        rate = e.get("rate")
        amount = e.get("amount")
        desc = e.get("description")
        entry_date = e.get("entry_date")

        lines.append(f"- Entry ID: {entry_id}")
        lines.append(f"  Attorney ID: {att_id}")
        lines.append(f"  Hours Billed: {safe(hours, '(missing)')}")
        lines.append(f"  Hourly Rate: {safe(rate, '(missing)')}")
        if amount and amount.strip():
            lines.append(f"  Amount: {amount}")
        else:
            lines.append("  Amount: (not provided in source)")
        # Lexical drift for descriptions in noisy files
        if is_noisy and desc:
            alt_desc_map = {
                "Reviewed contract": [
                    "analyzed the underlying agreement documents",
                    "examined deal paperwork",
                    "detailed review of transactional terms",
                ],
                "Drafted motion": [
                    "prepared substantive court application",
                    "developed motion papers",
                    "crafted pleading for judicial filing",
                ],
                "Prepared discovery": [
                    "organized evidentiary materials",
                    "assembled disclosure set",
                    "curated discovery production",
                ],
                "Client call": [
                    "strategic consultation with client",
                    "advisory conference with corporate representative",
                    "status alignment call with client team",
                ],
            }
            desc_alts = None
            for key, vals in alt_desc_map.items():
                if key.lower() in desc.lower():
                    desc_alts = vals
                    break
            if desc_alts:
                desc_noisy = random.choice(desc_alts)
            else:
                desc_noisy = desc
            lines.append(f"  Work Description: {desc_noisy}")
            lines.append(f"  Original Description: {desc}")
        else:
            lines.append(f"  Work Description: {safe(desc)}")

        lines.append(f"  Entry Date (raw): {safe(entry_date)}")
        lines.append("")

    # Totals
    lines.append("[Totals]")
    lines.append(f"Total Hours (reported): {hours_display}")
    lines.append(f"Total Amount (reported): {amount_display}")
    if is_noisy:
        lines.append(
            "Note: reported totals may not align exactly with line items due to "
            "rounding, internal write‑offs, or legacy system sync issues."
        )
    else:
        lines.append("Note: reported totals are expected to match the sum of entries.")
    lines.append("")

    # Narrative summary
    if is_noisy:
        narrative = (
            f"This dossier summarizes time entries for what is sometimes described as "
            f"'{matter_title_noisy}' involving {client_name_noisy}, a corporate entity in "
            f"the {safe(industry, 'commercial')} space. Terminology and identifiers may "
            f"vary across systems (e.g., {matter_alias} vs {real_matter_id}; "
            f"{alt_client_id} vs {real_client_id}), and internal notes may reference "
            f"phases or initiatives not present in the primary matter management schema."
        )
    else:
        narrative = (
            f"This file consolidates billing activity for matter {real_matter_id} "
            f"('{matter_title_clean}') on behalf of client {client_name_clean}. "
            f"It is intended to be a consistent, canonical view aligned with the "
            f"structured matters and client records."
        )
    lines.append("[Narrative Summary]")
    lines.append(narrative)
    lines.append("")

    return "\n".join(lines)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load source data
    billing_rows = read_csv_dict(os.path.join(PACK_DIR, "billing_entries_A.csv"))
    matters_rows = read_csv_dict(os.path.join(PACK_DIR, "matters_A.csv"))
    clients_rows = read_csv_dict(os.path.join(PACK_DIR, "structured_clients_A.csv"))

    matters_by_id = {row["matter_id"]: row for row in matters_rows}
    clients_by_id = {row["client_id"]: row for row in clients_rows}

    # Group billing entries by file_id (matter)
    billings_by_file: Dict[str, List[Dict[str, str]]] = {}
    for row in billing_rows:
        fid = row.get("file_id")
        if not fid:
            continue
        billings_by_file.setdefault(fid, []).append(row)

    file_ids = list(billings_by_file.keys())
    noisy_file_ids, format_map, sorted_file_ids = choose_noisy_and_formats(file_ids)

    # Generate one file per file_id
    for fid in sorted_file_ids:
        entries = billings_by_file[fid]
        matter = matters_by_id.get(fid, {})
        client_id = matter.get("client_ref")
        client = clients_by_id.get(client_id, {})

        is_noisy = fid in noisy_file_ids
        simulated_format = format_map[fid]

        content = build_content_for_matter(
            file_id=fid,
            entries=entries,
            matter=matter,
            client=client,
            is_noisy=is_noisy,
            simulated_format=simulated_format,
            all_clients=clients_by_id,
            all_file_ids=sorted_file_ids,
        )

        out_path = os.path.join(OUTPUT_DIR, f"{fid}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(
            f"Wrote {out_path} "
            f"(noisy={is_noisy}, simulated_format={simulated_format}, "
            f"entries={len(entries)})"
        )


if __name__ == "__main__":
    main()



