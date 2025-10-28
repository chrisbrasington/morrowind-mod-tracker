#!/usr/bin/env python3
import sys
import re
from collections import defaultdict

TABLE_HEADER_SOURCE = ["Name", "Notes", "URL", "Files", "Paths"]
TABLE_HEADER_TARGET = ["Type", "Name", "Description"]

def extract_url(text):
    """Extract URL from markdown link [text](url) or return text if no link"""
    match = re.search(r"\(([^)]+)\)", text)
    return match.group(1).strip() if match else text.strip()

def extract_name(text):
    """Extract name from markdown link [name](url) or return text if no link"""
    match = re.search(r"\[([^\]]+)\]", text)
    return match.group(1).strip() if match else text.strip()

def parse_table(lines, headers):
    """Parse markdown table into list of dicts"""
    mods = []
    header_regex = re.compile(r"\|\s*" + r"\s*\|\s*".join(headers) + r"\s*\|", re.IGNORECASE)
    
    i = 0
    while i < len(lines):
        if header_regex.match(lines[i].strip()):
            i += 2  # skip header + separator
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [col.strip() for col in lines[i].strip().strip("|").split("|")]
                if len(row) >= len(headers):
                    mods.append(dict(zip(headers, row)))
                i += 1
            break
        i += 1
    return mods

def load_markdown(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines()

def write_markdown(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def extract_sections(lines):
    """Split markdown by headers and preserve section names"""
    sections = {}
    current_section = None
    for line in lines:
        if line.startswith("#"):
            current_section = line
            sections[current_section] = [line]
        elif current_section:
            sections[current_section].append(line)
    return sections

def get_section_type(section_header):
    """Extract type from section header like '# Animation' -> 'Animation'"""
    return section_header.lstrip('#').strip()

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_modlist.py README_table.md MODLIST.md")
        sys.exit(1)

    source_path, target_path = sys.argv[1], sys.argv[2]

    # Load files
    src_lines = load_markdown(source_path)
    tgt_lines = load_markdown(target_path)

    # Parse source mods - URL comes from URL column (as markdown link)
    src_mods = parse_table(src_lines, TABLE_HEADER_SOURCE)
    src_sections = extract_sections(src_lines)
    
    # Build URL -> mod mapping from source, track which section each came from
    src_by_url = {}
    for section_header, section_lines in src_sections.items():
        section_mods = parse_table(section_lines, TABLE_HEADER_SOURCE)
        section_type = get_section_type(section_header)
        
        for mod in section_mods:
            url = extract_url(mod.get("URL", ""))
            name = extract_name(mod.get("Name", ""))
            if url:
                src_by_url[url] = {
                    "type": section_type,
                    "name": name,
                    "description": mod.get("Notes", ""),
                    "url": url
                }

    # Parse target sections
    tgt_sections = extract_sections(tgt_lines)
    
    # Find or create "Other Mods" section
    other_section = next((s for s in tgt_sections if "Other Mods" in s), None)
    if not other_section:
        other_section = "# Other Mods"
        tgt_sections[other_section] = [other_section]

    # Parse and update target mods, collect all existing URLs
    updated_sections = {}
    all_target_urls = set()
    
    for section, content in tgt_sections.items():
        tgt_mods = parse_table(content, TABLE_HEADER_TARGET)
        
        # Update existing mods - keep in current section but update all fields from source
        for mod in tgt_mods:
            url = extract_url(mod.get("Name", ""))
            all_target_urls.add(url)
            if url in src_by_url:
                src = src_by_url[url]
                # Update all fields but keep mod in its current section
                mod["Type"] = src["type"]
                mod["Name"] = f"[{src['name']}]({src['url']})"
                mod["Description"] = src["description"]
        
        updated_sections[section] = tgt_mods

    # Add new mods to "Other Mods" only if URL doesn't exist anywhere in target
    for url, src in src_by_url.items():
        if url not in all_target_urls:
            new_mod = {
                "Type": src["type"],
                "Name": f"[{src['name']}]({src['url']})",
                "Description": src["description"]
            }
            updated_sections[other_section].append(new_mod)
            all_target_urls.add(url)

    # Rebuild markdown
    output = []
    for section in tgt_sections.keys():
        output.append(section)
        mods = updated_sections.get(section, [])
        
        if mods:
            output.append("| " + " | ".join(TABLE_HEADER_TARGET) + " |")
            output.append("|" + "|".join(["------"] * len(TABLE_HEADER_TARGET)) + "|")
            for mod in mods:
                output.append(f"| {mod['Type']} | {mod['Name']} | {mod['Description']} |")
        
        output.append("")

    write_markdown(target_path, output)
    print(f"Updated: {target_path}")

if __name__ == "__main__":
    main()