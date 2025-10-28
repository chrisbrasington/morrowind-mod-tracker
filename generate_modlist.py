import sys
import re

def parse_table_lines(lines):
    rows = []
    for line in lines:
        m = re.match(r'\|\s*([^|]+)\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*(.*?)\s*\|', line)
        if m:
            type_, name, url, desc = m.groups()
            rows.append({
                "type": type_.strip(),
                "name": name.strip(),
                "url": url.strip(),
                "desc": desc.strip()
            })
    return rows

def merge_tables(readme_rows, modlist_content):
    modlist_lines = modlist_content.splitlines()
    existing_rows = parse_table_lines(modlist_lines)

    # Lookup by URL first, fallback to name
    url_map = {row["url"]: row for row in existing_rows}
    name_map = {row["name"]: row for row in existing_rows}

    # Find insertion point for Other Mods table
    other_mods_index = None
    for i, line in enumerate(modlist_lines):
        if line.strip().lower().startswith("# other mods"):
            other_mods_index = i
            break

    if other_mods_index is None:
        # Append Other Mods section if missing
        modlist_lines.append("\n# Other Mods\n")
        modlist_lines.append("| Type | Name | Description |")
        modlist_lines.append("|------|------|-------------|")
        other_mods_index = len(modlist_lines)

    insertion_index = other_mods_index + 3  # First row after header

    for row in readme_rows:
        existing = url_map.get(row["url"]) or name_map.get(row["name"])
        if existing:
            # Only update description if it's different
            if existing["desc"] != row["desc"]:
                # Replace description in the matching line
                pattern = rf'\|\s*{re.escape(existing["type"])}\s*\|\s*\[{re.escape(existing["name"])}\]\({re.escape(existing["url"])}\)\s*\|.*?\|'
                replacement = f'| {existing["type"]} | [{existing["name"]}]({existing["url"]}) | {row["desc"]} |'
                modlist_lines = [
                    re.sub(pattern, replacement, line)
                    if re.search(pattern, line) else line
                    for line in modlist_lines
                ]
        else:
            # Insert new mod into Other Mods
            new_line = f'| {row["type"]} | [{row["name"]}]({row["url"]}) | {row["desc"]} |'
            modlist_lines.insert(insertion_index, new_line)
            insertion_index += 1

    return "\n".join(modlist_lines)

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_modlist.py README_table.md MODLIST.md")
        return

    readme_file = sys.argv[1]
    modlist_file = sys.argv[2]

    readme_rows = parse_table_lines(open(readme_file).read().splitlines())
    modlist_content = open(modlist_file).read()

    merged = merge_tables(readme_rows, modlist_content)
    with open(modlist_file, "w") as f:
        f.write(merged)

    print("✅ MODLIST.md updated successfully!")

if __name__ == "__main__":
    main()
