#!/usr/bin/env python3
import sys
import re
from collections import defaultdict

TABLE_HEADER_SOURCE = ["Name", "Notes", "URL", "Files", "Paths"]
TABLE_HEADER_TARGET = ["Type", "Name", "Description"]

def parse_mod_table(lines, expected_headers):
    mods = []
    headers_line = "|" + "|".join(expected_headers) + "|"

    i = 0
    while i < len(lines):
        if lines[i].strip().replace(" ", "") == headers_line.replace(" ", ""):
            i += 2  # skip header + separator line
            while i < len(lines) and lines[i].startswith("|"):
                row = [col.strip() for col in lines[i].strip().strip("|").split("|")]
                if len(row) >= len(expected_headers):
                    mod = dict(zip(expected_headers, row))
                    mods.append(mod)
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
    """Extract all sections and their table content from MODLIST.md"""
    sections = defaultdict(list)
    current_section = None

    for line in lines:
        if line.startswith("# "):
            current_section = line
            sections[current_section].append(line)
        elif current_section:
            sections[current_section].append(line)

    return sections


def mod_key(mod):
    """Uniquely identify mods matching by name + URL"""
    return (mod.get("Name") or "").strip(), (mod.get("URL") or "").strip()


def convert_source_mod(src_mod, category="Other Mods"):
    return {
        "Type": category.replace("# ", "").strip(),
        "Name": src_mod["Name"],
        "Description": src_mod["Notes"]
    }


def update_or_append_mod(target_rows, src_mod, category_header):
    """Checks if mod exists: update description OR append into section"""
    src_key = mod_key(src_mod)

    # Try updating existing
    for row in target_rows:
        if mod_key(row) == src_key:
            row["Description"] = src_mod["Notes"]  # update description
            return

    # Append as new entry
    new_mod = convert_source_mod(src_mod, category_header)
    target_rows.append(new_mod)


def parse_target_tables(sections):
    """Parse tables in existing MODLIST.md into structured dict"""
    parsed = {}

    for section, content in sections.items():
        rows = parse_mod_table(content, TABLE_HEADER_TARGET)
        parsed[section] = rows

    return parsed


def rebuild_sections(sections, parsed_tables):
    """Rebuild markdown content with updated mod rows in each section"""
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
            # preserve sections with no mods
            for l in content[1:]:
                out.append(l)

        out.append("")  # spacing

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

    # Find "Other Mods" section or create one
    other_section = next((s for s in tgt_sections if "Other Mods" in s), "# Other Mods")
    if other_section not in tgt_sections:
        tgt_sections[other_section] = [other_section]
        tgt_mods_by_section[other_section] = []

    # Apply update/append logic
    for src_section, mods in src_mods_by_section.items():
        category_name = src_section.replace("##", "#").strip()  # convert to header
        for mod in mods:
            update_or_append_mod(
                tgt_mods_by_section[other_section], mod, category_name
            )

    # Rebuild new file
    updated = rebuild_sections(tgt_sections, tgt_mods_by_section)
    write_markdown(target_path, updated)

    print(f"Updated: {target_path}")


if __name__ == "__main__":
    main()
