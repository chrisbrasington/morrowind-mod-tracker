#!/usr/bin/env python3
import sys
import re
from collections import defaultdict

# Source table headers
TABLE_HEADER_SOURCE = ["Name", "Notes", "URL", "Files", "Paths"]
# Target table headers
TABLE_HEADER_TARGET = ["Type", "Name", "Description"]

def extract_name(name_field):
    """Strip markdown link: [Text](url) -> Text"""
    match = re.match(r"\[(.*?)\]", name_field)
    if match:
        return match.group(1).strip()
    return name_field.strip()

def mod_key(mod):
    """Return the normalized mod name for matching"""
    return extract_name(mod.get("Name", ""))

def parse_mod_table(lines, expected_headers):
    """Parse markdown table into list of dicts"""
    mods = []
    headers_line = "|" + "|".join(expected_headers) + "|"
    i = 0
    while i < len(lines):
        if lines[i].strip().replace(" ", "") == headers_line.replace(" ", ""):
            i += 2  # skip header + separator
            while i < len(lines) and lines[i].startswith("|"):
                row = [col.strip() for col in lines[i].strip().strip("|").split("|")]
                if len(row) >= len(expected_headers):
                    mods.append(dict(zip(expected_headers, row)))
                i += 1
        else:
            i += 1
    return mods

def load_markdown(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines()

def write_markdown(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def extract_sections(lines):
    """Split markdown by headers (# ...)"""
    sections = defaultdict(list)
    current_section = None
    for line in lines:
        if line.startswith("# "):
            current_section = line
            sections[current_section].append(line)
        elif current_section:
            sections[current_section].append(line)
    return sections

def convert_source_mod(src_mod, category="Other Mods"):
    return {
        "Type": category.replace("#", "").strip(),
        "Name": f"[{src_mod['Name']}]({src_mod['URL']})",
        "Description": src_mod["Notes"]
    }

def update_or_append_mod_all_sections(tgt_mods_by_section, src_mod, category_name):
    src_name = mod_key(src_mod)
    # Try updating in any section first
    for section, rows in tgt_mods_by_section.items():
        for row in rows:
            if mod_key(row) == src_name:
                row["Description"] = src_mod["Notes"]
                return
    # If not found anywhere, append to "Other Mods"
    other_section = next((s for s in tgt_mods_by_section if "Other Mods" in s), "# Other Mods")
    new_mod = convert_source_mod(src_mod, category_name)
    tgt_mods_by_section[other_section].append(new_mod)

def parse_target_tables(sections):
    """Parse tables in existing MODLIST.md"""
    parsed = {}
    for section, content in sections.items():
        rows = parse_mod_table(content, TABLE_HEADER_TARGET)
        parsed[section] = rows
    return parsed

def rebuild_sections(sections, parsed_tables):
    """Rebuild markdown with updated tables"""
    out = []
    for section, content in sections.items():
        out.append(section)
        rows = parsed_tables.get(section, [])
        if rows:
            out.append("| " + " | ".join(TABLE_HEADER_TARGET) + " |")
            out.append("|" + "|".join(["------"] * len(TABLE_HEADER_TARGET)) + "|")
            for r in rows:
                out.append(f"| {r['Type']} | {r['Name']} | {r['Description']} |")
        else:
            # preserve blank sections
            for l in content[1:]:
                out.append(l)
        out.append("")
    return out

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_modlist.py README_table.md MODLIST.md")
        sys.exit(1)

    source_path, target_path = sys.argv[1], sys.argv[2]

    src_lines = load_markdown(source_path)
    tgt_lines = load_markdown(target_path)

    src_sections = extract_sections(src_lines)
    tgt_sections = extract_sections(tgt_lines)

    # Parse tables
    src_mods_by_section = {
        sec: parse_mod_table(lines, TABLE_HEADER_SOURCE)
        for sec, lines in src_sections.items()
    }

    tgt_mods_by_section = parse_target_tables(tgt_sections)

    # Find or create "Other Mods"
    other_section = next((s for s in tgt_sections if "Other Mods" in s), "# Other Mods")
    if other_section not in tgt_sections:
        tgt_sections[other_section] = [other_section]
        tgt_mods_by_section[other_section] = []

    # Update descriptions or append new mods
    for src_section, mods in src_mods_by_section.items():
        category_name = src_section.replace("##", "#").strip()
        for mod in mods:
            update_or_append_mod_all_sections(tgt_mods_by_section, mod, category_name)

    updated = rebuild_sections(tgt_sections, tgt_mods_by_section)
    write_markdown(target_path, updated)
    print(f"Updated: {target_path}")

if __name__ == "__main__":
    main()
