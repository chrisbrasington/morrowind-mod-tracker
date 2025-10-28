import sys
import re
from collections import defaultdict

TABLE_HEADER = "| Type | Name | Description |"
URL_REGEX = re.compile(r'\[(.*?)\]\((https?://[^\)]+)\)')

def parse_table(lines):
    """Extract rows as dict: {type: {url: (name, desc)}}"""
    mods = defaultdict(dict)

    for line in lines:
        line = line.strip()
        if not line.startswith("|") or line.startswith("| Type"):
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue

        mod_type, name_col, desc = parts[1:4]
        match = URL_REGEX.search(name_col)
        if not match:
            continue

        name = match.group(1)
        url = match.group(2)

        mods[mod_type][url] = (name, desc)

    return mods


def load_modlist(path):
    """Load MODLIST.md into sections dict {section_name: [lines]}"""
    sections = {}
    current = None
    lines_buffer = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("# "):
                if current:
                    sections[current] = lines_buffer
                current = line.strip()[2:]
                lines_buffer = []
            else:
                if current:
                    lines_buffer.append(line.rstrip("\n"))

        if current:
            sections[current] = lines_buffer

    return sections


def extract_existing_mods(sections):
    """Return lookup dicts by URL and by Name"""
    by_url = {}
    by_name = {}

    for section, lines in sections.items():
        for idx, line in enumerate(lines):
            match = URL_REGEX.search(line)
            if match:
                name = match.group(1)
                url = match.group(2)
                by_url[url] = (section, idx, name)
                by_name[name] = (section, idx, url)

    return by_url, by_name


def merge_mods(sections, new_mods):
    by_url, by_name = extract_existing_mods(sections)

    # Ensure Other Mods exists
    if "Other Mods" not in sections:
        sections["Other Mods"] = [TABLE_HEADER, "|------|------|-------------|"]

    for mod_type, entries in new_mods.items():
        for url, (name, desc) in entries.items():

            if url in by_url:
                # ✅ URL match = same mod, update existing
                section, idx, old_name = by_url[url]
                line = sections[section][idx]
                parts = [p.strip() for p in line.split("|")]

                old_desc = parts[3] if len(parts) > 3 else ""

                if name != old_name or desc != old_desc:
                    sections[section][idx] = f"| {mod_type} | [{name}]({url}) | {desc} |"
                continue

            if name in by_name:
                # ✅ Name match but URL mismatch = consider same mod name → skip new
                continue

            # ✅ New mod → add it
            row = f"| {mod_type} | [{name}]({url}) | {desc} |"
            if mod_type not in sections:
                sections["Other Mods"].append(row)
            else:
                sections[mod_type].append(row)

    return sections


def write_modlist(path, sections):
    with open(path, "w", encoding="utf-8") as f:
        for section, lines in sections.items():
            f.write(f"# {section}\n")
            for line in lines:
                f.write(line + "\n")
            f.write("\n")


def generate_modlist(readme_table_path, modlist_path):
    sections = load_modlist(modlist_path)

    with open(readme_table_path, "r", encoding="utf-8") as f:
        readme_lines = f.readlines()

    new_mods = parse_table(readme_lines)
    updated_sections = merge_mods(sections, new_mods)

    write_modlist(modlist_path, updated_sections)
    print(f"✅ MODLIST.md updated successfully (based on URL or Name matching)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_modlist.py README_table.md MODLIST.md")
        sys.exit(1)

    generate_modlist(sys.argv[1], sys.argv[2])
