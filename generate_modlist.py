import sys
import re
from collections import defaultdict

TABLE_HEADER = "| Type | Name | Description |"
URL_REGEX = re.compile(r'\[(.*?)\]\((https?://[^\)]+)\)')

def parse_table(lines):
    """Extract rows as dict: {type: [(name, url, desc)]}"""
    mods = defaultdict(list)
    for line in lines:
        line = line.strip()
        if not line.startswith("|") or line.startswith("| Type"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue
        mod_type, name_col, desc = parts[1:4]
        name_match = URL_REGEX.search(name_col)
        if not name_match:
            continue
        name = name_match.group(1)
        url = name_match.group(2)
        mods[mod_type].append((name, url, desc))
    return mods

def load_modlist(path):
    """Load MODLIST.md into {section_name: [lines]}"""
    sections = {}
    current_section = None
    section_lines = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("# "):
                if current_section:
                    sections[current_section] = section_lines
                current_section = line.strip()[2:]
                section_lines = []
            else:
                if current_section:
                    section_lines.append(line.rstrip("\n"))
        if current_section:
            sections[current_section] = section_lines
    return sections

def extract_existing_mods(sections):
    existing = set()
    for section in sections.values():
        for line in section:
            match = URL_REGEX.search(line)
            if match:
                existing.add(match.group(1))
    return existing

def merge_mods(modlist_sections, new_mods):
    existing = extract_existing_mods(modlist_sections)
    if "Other Mods" not in modlist_sections:
        modlist_sections["Other Mods"] = [TABLE_HEADER, "|------|------|-------------|"]
    updated = {s: list(lines) for s, lines in modlist_sections.items()}

    for mod_type, entries in new_mods.items():
        for name, url, desc in entries:
            if name in existing:
                continue
            row = f"| {mod_type} | [{name}]({url}) | {desc} |"
            if mod_type in updated:
                updated[mod_type].append(row)
            else:
                updated["Other Mods"].append(row)
    return updated

def write_modlist(path, sections):
    with open(path, "w", encoding="utf-8") as f:
        for sec_name, lines in sections.items():
            f.write(f"# {sec_name}\n")
            for line in lines:
                f.write(line + "\n")
            f.write("\n")

def generate_modlist(readme_table_path, modlist_path):
    modlist_sections = load_modlist(modlist_path)
    with open(readme_table_path, "r", encoding="utf-8") as f:
        readme_lines = f.readlines()
    new_mods = parse_table(readme_lines)
    updated_sections = merge_mods(modlist_sections, new_mods)
    write_modlist(modlist_path, updated_sections)
    print(f"✅ MODLIST.md updated with new mods from {readme_table_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_modlist.py README_table.md MODLIST.md")
        sys.exit(1)
    readme_table_file = sys.argv[1]
    modlist_file = sys.argv[2]
    generate_modlist(readme_table_file, modlist_file)
