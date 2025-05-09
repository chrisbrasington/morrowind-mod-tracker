import os
import re
from pathlib import Path
from collections import defaultdict
import markdown
import hashlib

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
                if file.lower().endswith((".esp", ".esm")):
                    content_map[file] = Path(root)
    return content_map

def get_section_name(path):
    # Use the relative part of the path to categorize
    parts = Path(path).parts
    try:
        index = parts.index("morrowind") + 1
        return parts[index] if index < len(parts) else "Uncategorized"
    except ValueError:
        return parts[-2] if len(parts) > 1 else "Uncategorized"

def load_existing_readme(path):
    if not path.exists():
        return defaultdict(dict)
    
    section_pattern = re.compile(r"^## (.+)")
    row_pattern = re.compile(r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|")

    sections = defaultdict(dict)
    current_section = None

    with open(path, "r") as f:
        for line in f:
            section_match = section_pattern.match(line)
            row_match = row_pattern.match(line)
            if section_match:
                current_section = section_match.group(1)
            elif row_match and current_section:
                mod, content = row_match.groups()
                content_list = [x.strip() for x in content.split(",")]
                sections[current_section][mod] = set(content_list)
    return sections

def generate_readme_data(data_dirs, content_files, content_map):
    output = defaultdict(lambda: defaultdict(set))

    for esp in content_files:
        if esp not in content_map:
            continue
        mod_path = content_map[esp]
        mod_root = None
        for base in data_dirs:
            if str(mod_path).startswith(base):
                rel_path = Path(mod_path).relative_to(base)
                mod_root = rel_path.parts[0] if rel_path.parts else "Unknown"
                break
        section = get_section_name(str(mod_path))
        output[section][mod_root].add(esp)
    return output

def update_readme(existing, generated):
    lines = []

    for section in sorted(generated.keys()):
        lines.append(f"## {section}\n")
        lines.append("| Mod Name | Content Files |")
        lines.append("|----------|----------------|")

        for mod in sorted(generated[section].keys()):
            new_contents = generated[section][mod]
            existing_contents = existing.get(section, {}).get(mod, set())
            combined = existing_contents.union(new_contents)
            content_str = ", ".join(sorted(combined))
            lines.append(f"| {mod} | {content_str} |")

        lines.append("")

    with open(README_PATH, "w") as f:
        f.write("\n".join(lines))

def main():
    data_dirs, content_files = parse_openmw_cfg(OPENMW_CFG)
    content_map = find_content_paths(data_dirs)
    existing = load_existing_readme(README_PATH)
    generated = generate_readme_data(data_dirs, content_files, content_map)

    # Merge new data with existing
    for section in generated:
        for mod in generated[section]:
            existing[section][mod] = existing[section].get(mod, set()).union(generated[section][mod])

    update_readme(existing, generated)
    print("README.md updated.")

if __name__ == "__main__":
    main()
