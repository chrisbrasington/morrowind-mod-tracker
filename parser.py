import os
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
    row_pattern = re.compile(r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|")

    sections = defaultdict(list)
    current_section = None

    with open(path, "r") as f:
        for line in f:
            section_match = section_pattern.match(line)
            row_match = row_pattern.match(line)
            if section_match:
                current_section = section_match.group(1)
            elif row_match and current_section:
                mod, content, paths = row_match.groups()
                sections[current_section].append((mod, content, paths))
    return sections

def generate_readme_data(data_dirs, content_files, content_map):
    output = defaultdict(list)

    for esp in content_files:
        if esp not in content_map:
            print(f"[WARN] Could not find ESP on disk: {esp}")
            continue

        mod_path = content_map[esp]
        mod_root = None
        matched_paths = []

        for base in data_dirs:
            if str(mod_path).startswith(base):
                rel_path = Path(mod_path).relative_to(base)
                mod_root = rel_path.parts[0] if rel_path.parts else Path(mod_path).name
                matched_paths.append(base)

        if not mod_root:
            mod_root = Path(mod_path).name

        section = get_section_name(str(mod_path))

        print(f"[INFO] Section: {section} | Mod: {mod_root} | ESP: {esp} | Path(s): {matched_paths or [str(mod_path)]}")

        for base in matched_paths or [str(mod_path)]:
            output[section].append((mod_root, esp, base))

    return output


def update_readme(existing, generated):
    merged = defaultdict(set)

    # Merge existing and generated rows into one combined set
    for section in set(existing.keys()).union(generated.keys()):
        for row in existing.get(section, []):
            merged[section].add(row)
        for row in generated.get(section, []):
            merged[section].add(row)

    lines = []
    for section in sorted(merged.keys()):
        lines.append(f"## {section}\n")
        lines.append("| Mod Name | Notes | Content File | Paths Used |")
        lines.append("|----------|-------|--------------|-------------|")

        for mod_name, content_file, path_used in sorted(merged[section]):
            lines.append(f"| {mod_name} |  | {content_file} | {path_used} |")

        lines.append("")

    with open(README_PATH, "w") as f:
        f.write("\n".join(lines))


def main():
    data_dirs, content_files = parse_openmw_cfg(OPENMW_CFG)
    content_map = find_content_paths(data_dirs)
    existing = load_existing_readme(README_PATH)
    generated = generate_readme_data(data_dirs, content_files, content_map)

    # Merge generated with existing for idempotency
    for section in generated:
        existing[section].extend(generated[section])

    update_readme(existing, generated)
    print("README.md updated.")

if __name__ == "__main__":
    main()
