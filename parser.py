import os, sys
import re
from pathlib import Path
from collections import defaultdict

OPENMW_CFG = Path.home() / ".config/openmw/openmw.cfg"
README_PATH = Path("README.md")

def parse_openmw_cfg(cfg_path):
    data_dirs = []
    content_files = []
    with open(cfg_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("data="):
                data_dirs.append(line.split("=", 1)[1].strip('"'))
            elif line.startswith("content="):
                content_files.append(line.split("=", 1)[1])
    return data_dirs, content_files

def find_content_paths(data_dirs):
    content_map = {}
    for base_dir in data_dirs:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith((".esp", ".esm", "omwscripts")):
                    content_map[file] = Path(root)
    return content_map

def get_section_name(path):
    parts = Path(path).parts
    try:
        index = parts.index("morrowind") + 1
        return parts[index] if index < len(parts) else parts[-1]
    except ValueError:
        return parts[-2] if len(parts) > 1 else parts[-1]

def load_existing_readme(path):
    if not path.exists():
        return defaultdict(list)
    
    section_pattern = re.compile(r"^## (.+)")
    row_pattern = re.compile(r"^\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|")

    sections = defaultdict(list)
    current_section = None

    with open(path, "r") as f:
        for line in f:
            section_match = section_pattern.match(line)
            row_match = row_pattern.match(line)
            if section_match:
                current_section = section_match.group(1)
            elif row_match and current_section:
                mod, notes, content, paths = row_match.groups()
                sections[current_section].append((mod, notes, content, paths))

    return sections

def generate_readme_data(data_dirs, content_files, content_map):
    output = defaultdict(list)

    for esp in content_files:
        if esp not in content_map:
            print(f"[WARN] Could not find ESP on disk: {esp}")
            continue

        mod_path = content_map[esp]
        matched_paths = []

        section = get_section_name(str(mod_path))
        mod_root = None

        for base in data_dirs:
            if str(mod_path).startswith(base):
                base_parts = Path(base).parts
                mod_parts = Path(mod_path).parts
                try:
                    section_index = mod_parts.index(section)
                    mod_root = "/".join(mod_parts[section_index + 1:])
                    matched_paths.append(base)
                    break  # only use the first match
                except ValueError:
                    continue

        if not mod_root:
            mod_root = Path(mod_path).name
            matched_paths = [str(mod_path)]

        print(f"[INFO] Section: {section} | Mod: {mod_root} | ESP: {esp} | Path(s): {matched_paths}")

        for base in matched_paths:
            output[section].append((mod_root, "", esp, base))  # (mod_name, notes, content_file, path_used)

    return output

def update_readme(existing, generated):
    # Create a merged dictionary that will hold all rows for the sections
    merged = defaultdict(list)

    # Copy over all existing rows to the merged dictionary
    for section, rows in existing.items():
        for row in rows:
            # Skip headers or dividers
            if row[0].startswith("Mod Name") or row[0].startswith("---"):
                # Ensure each row has 4 elements
                if len(row) == 3:
                    row = (row[0], "", row[1], row[2])  # Add empty notes
                continue
            else:
                merged[section].append(row)

    # Process the generated rows
    for section, rows in generated.items():
        for mod_name, notes, content_file, path_used in rows:
            # Check if content_file already exists (should compare against row[2])
            if any(row[2] == content_file for row in merged[section]):
                continue

            # Add new row
            merged[section].append((mod_name, "", content_file, path_used))

    # for r in merged['Architecture']:
    #     print(r)
    # sys.exit()

    lines = []

    for section in sorted(merged.keys()):
        if merged[section]:
            lines.append(f"## {section}\n")
            lines.append("| Mod Name | Notes | Content File(s) | Paths Used |")
            lines.append("|----------|-------|------------------|-------------|")

            # Group by (mod_name, notes)
            grouped = defaultdict(list)
            for mod_name, notes, content_file, path in merged[section]:
                grouped[(mod_name, notes)].append((content_file, path))

            for (mod_name, notes), entries in sorted(grouped.items()):
                content_files = ", ".join(sorted({esp for esp, _ in entries}))
                paths_used = ", ".join(sorted({path for _, path in entries}))
                lines.append(f"| {mod_name} | {notes} | {content_files} | {paths_used} |")

            lines.append("")

    # Write the updated content to the README
    with open(README_PATH, "w") as f:
        f.write("\n".join(lines))

def main():
    data_dirs, content_files = parse_openmw_cfg(OPENMW_CFG)
    content_map = find_content_paths(data_dirs)
    existing = load_existing_readme(README_PATH)
    generated = generate_readme_data(data_dirs, content_files, content_map)

    # # Merge generated with existing for idempotency
    # for section in generated:
    #     existing[section].extend(generated[section])

    update_readme(existing, generated)
    print("README.md updated.")

if __name__ == "__main__":
    main()
