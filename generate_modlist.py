#!/usr/bin/env python3
import sys
import re
from collections import OrderedDict

# Strict row regex: captures Type, link text (Name), URL, Description
ROW_RE = re.compile(r'^\|\s*(?P<type>[^|]+?)\s*\|\s*\[(?P<name>[^\]]+)\]\((?P<url>https?://[^\)]+)\)\s*\|\s*(?P<desc>.*?)\s*\|$')

TABLE_HEADER = "| Type | Name | Description |"
TABLE_DIVIDER = "|------|------|-------------|"

def parse_readme_rows(lines):
    rows = []
    for ln in lines:
        m = ROW_RE.match(ln.strip())
        if m:
            rows.append({
                "type": m.group("type").strip(),
                "name": m.group("name").strip(),
                "url": m.group("url").strip(),
                "desc": m.group("desc").strip()
            })
    return rows

def load_modlist_sections(path):
    """Return OrderedDict of sections -> list(lines) preserving order"""
    sections = OrderedDict()
    current = None
    buf = []

    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if line.startswith("# "):
                if current is not None:
                    sections[current] = buf
                current = line[2:].strip()
                buf = []
            else:
                if current is not None:
                    buf.append(line)
                else:
                    # Lines before first section - keep under empty name
                    sections.setdefault("", []).append(line)
        if current is not None:
            sections[current] = buf

    return sections

def build_lookup(sections):
    """Return two dicts: by_url[url] -> (section, idx), by_name[name] -> (section, idx)"""
    by_url = {}
    by_name = {}
    for sec, lines in sections.items():
        for idx, ln in enumerate(lines):
            m = ROW_RE.match(ln.strip())
            if not m:
                continue
            url = m.group("url").strip()
            name = m.group("name").strip()
            by_url[url] = (sec, idx)
            # If multiple same names exist, first wins (fallback)
            if name not in by_name:
                by_name[name] = (sec, idx)
    return by_url, by_name

def ensure_other_mods(sections):
    if "Other Mods" not in sections:
        sections["Other Mods"] = [TABLE_HEADER, TABLE_DIVIDER]
    else:
        # ensure a header exists in that section if empty
        lines = sections["Other Mods"]
        if not lines or not any(l.strip().startswith("| Type") for l in lines):
            sections["Other Mods"] = [TABLE_HEADER, TABLE_DIVIDER] + [l for l in lines if l.strip() != ""]
    return sections

def merge(readme_rows, sections):
    by_url, by_name = build_lookup(sections)

    added = 0
    updated = 0
    skipped = 0

    sections = ensure_other_mods(sections)

    # We'll modify sections in place
    for row in readme_rows:
        url = row["url"]
        name = row["name"]
        new_desc = row["desc"]

        if url in by_url:
            sec, idx = by_url[url]
            orig_line = sections[sec][idx]
            m = ROW_RE.match(orig_line.strip())
            if not m:
                # weird line; replace conservatively
                sections[sec][idx] = f"| {row['type']} | [{row['name']}]({url}) | {new_desc} |"
                updated += 1
                continue

            orig_type = m.group("type").strip()
            orig_name = m.group("name").strip()
            orig_desc = m.group("desc").strip()

            if orig_desc.strip() != new_desc.strip():
                sections[sec][idx] = f"| {orig_type} | [{orig_name}]({url}) | {new_desc.strip()} |"
                updated += 1
            else:
                # No real change — leave the row untouched
                skipped += 1
                continue
            # ensure we won't process duplicates later
            continue

        if name in by_name:
            # name exists but url differs -> treat as same mod name: update description only
            sec, idx = by_name[name]
            orig_line = sections[sec][idx]
            m = ROW_RE.match(orig_line.strip())
            if not m:
                sections[sec][idx] = f"| {row['type']} | [{row['name']}]({url}) | {new_desc} |"
                updated += 1
                continue

            orig_type = m.group("type").strip()
            orig_name = m.group("name").strip()
            orig_url = m.group("url").strip()
            orig_desc = m.group("desc").strip()

            # Update description, but keep orig_type and orig_name and orig_url (do not change name/type)
            if orig_desc != new_desc:
                sections[sec][idx] = f"| {orig_type} | [{orig_name}]({orig_url}) | {new_desc} |"
                updated += 1
            else:
                skipped += 1
            continue

        # Not found -> append to Other Mods
        new_line = f"| {row['type']} | [{row['name']}]({url}) | {new_desc} |"
        sections["Other Mods"].append(new_line)
        added += 1
        # update lookups so repeated entries in README_table.md won't duplicate
        by_url[url] = ("Other Mods", len(sections["Other Mods"]) - 1)
        if row["name"] not in by_name:
            by_name[row["name"]] = ("Other Mods", len(sections["Other Mods"]) - 1)

    return sections, added, updated, skipped

def write_sections(path, sections):
    with open(path, "w", encoding="utf-8") as fh:
        for i, (sec, lines) in enumerate(sections.items()):
            # Strip trailing blank lines inside a section
            while lines and not lines[-1].strip():
                lines.pop()

            # Section header
            if sec:
                fh.write(f"# {sec}\n")

            # Write section content
            for ln in lines:
                fh.write(ln.rstrip() + "\n")

            # Only add ONE blank line between sections, and not after final section
            if i < len(sections) - 1:
                fh.write("\n")

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_modlist.py README_table.md MODLIST.md")
        sys.exit(1)

    readme_table = sys.argv[1]
    modlist = sys.argv[2]

    with open(readme_table, "r", encoding="utf-8") as fh:
        readme_lines = fh.read().splitlines()

    with open(modlist, "r", encoding="utf-8") as fh:
        _ = fh.read()  # validate exists

    readme_rows = parse_readme_rows(readme_lines)
    sections = load_modlist_sections(modlist)

    merged_sections, added, updated, skipped = merge(readme_rows, sections)
    write_sections(modlist, merged_sections)

    print(f"Done. added={added} updated={updated} skipped={skipped}")

if __name__ == "__main__":
    main()
