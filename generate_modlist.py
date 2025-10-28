#!/usr/bin/env python3
import sys
import re
from collections import defaultdict

TABLE_HEADER_SOURCE = ["Name", "Notes", "URL", "Files", "Paths"]
TABLE_HEADER_TARGET = ["Type", "Name", "Description"]

def normalize_url(url):
    """Normalize URL - if it's just a number, convert to full Nexus URL"""
    url = url.strip()
    if url.isdigit():
        return f"https://www.nexusmods.com/morrowind/mods/{url}"
    return url

def extract_url(text):
    """Extract URL from markdown link or return text if no link"""
    match = re.search(r"\(([^)]+)\)", text)
    url = match.group(1).strip() if match else text.strip()
    return normalize_url(url)

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
    """Split markdown by headers"""
    sections = {}
    current_section = None
    for line in lines:
        if line.startswith("# "):
            current_section = line
            sections[current_section] = [line]
        elif current_section:
            sections[current_section].append(line)
    return sections

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_modlist.py README_table.md MODLIST.md")
        sys.exit(1)

    source_path, target_path = sys.argv[1], sys.argv[2]

    # Load files
    src_lines = load_markdown(source_path)
    tgt_lines = load_markdown(target_path)

    # Parse source mods - URL comes from URL column
    src_mods = parse_table(src_lines, TABLE_HEADER_SOURCE)
    
    # Build URL -> mod mapping from source
    src_by_url = {}
    for mod in src_mods:
        url = normalize_url(mod.get("URL", ""))  # Normalize URL (handles mod IDs)
        if url:
            src_by_url[url] = mod

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
        
        # Update existing mods and track all URLs in target
        for mod in tgt_mods:
            url = extract_url(mod.get("Name", ""))  # Extract URL from markdown link
            all_target_urls.add(url)
            if url in src_by_url:
                mod["Description"] = src_by_url[url]["Notes"]
        
        updated_sections[section] = tgt_mods

    # Add new mods to "Other Mods" only if URL doesn't exist anywhere in target
    for url, src_mod in src_by_url.items():
        if url not in all_target_urls:
            new_mod = {
                "Type": "Mod",
                "Name": f"[{src_mod['Name']}]({url})",
                "Description": src_mod["Notes"]
            }
            updated_sections[other_section].append(new_mod)
            all_target_urls.add(url)  # Track it to prevent duplicates within this run

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