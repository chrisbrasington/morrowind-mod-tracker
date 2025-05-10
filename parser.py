from pathlib import Path

# Full implementation of parser.py with support for:
# - Texture-only mods (no content files)
# - Grouping data directories under mod names
# - Alphabetical sorting of mods in sections
# - Merging README.md and GENERATED.md without duplication

import os
import re
import shutil
from pathlib import Path
from collections import defaultdict
from typing import List, Dict

OPENMW_CFG = Path.home() / ".config/openmw/openmw.cfg"
LOCAL_CFG_COPY = Path("./openmw.cfg")
README_PATH = Path("README.md")
GENERATED_PATH = Path("GENERATED.md")
MERGED_PATH = Path("MERGED.md")


class ModEntry:
    def __init__(self, mod_name: str, notes: str = "", content_files: List[str] = None, paths_used: List[str] = None):
        self.mod_name = mod_name
        self.notes = notes
        self.content_files = sorted(set(content_files or []))
        self.paths_used = sorted(set(paths_used or []))

    def merge(self, other):
        self.content_files = sorted(set(self.content_files + other.content_files))
        self.paths_used = sorted(set(self.paths_used + other.paths_used))

    def __eq__(self, other):
        return set(self.content_files) == set(other.content_files)

    def __hash__(self):
        return hash(tuple(sorted(self.content_files)))


class ModSection:
    def __init__(self, name: str):
        self.name = name
        self.entries: Dict[str, ModEntry] = {}

    def add_or_merge_entry(self, entry: ModEntry):
        key = entry.mod_name
        if key in self.entries:
            self.entries[key].merge(entry)
        else:
            self.entries[key] = entry

    def sorted_entries(self):
        return [self.entries[k] for k in sorted(self.entries.keys())]


def parse_openmw_cfg(cfg_path: Path):
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


def get_section_name(path: str):
    parts = Path(path).parts
    try:
        index = parts.index("morrowind") + 1
        return parts[index] if index < len(parts) else parts[-1]
    except ValueError:
        return parts[-2] if len(parts) > 1 else parts[-1]


def get_mod_name(path: str, section: str):
    parts = Path(path).parts
    try:
        section_index = parts.index(section)
        if section_index + 1 < len(parts):
            return parts[section_index + 1]
        else:
            return parts[section_index]  # fallback to section name
    except ValueError:
        return parts[-1]  # fallback if section not in path


def generate_mod_sections(data_dirs, content_files, content_map):
    sections: Dict[str, ModSection] = {}

    # Track all content files
    for esp in content_files:
        if esp not in content_map:
            print(f"[WARN] Could not find ESP on disk: {esp}")
            continue

        mod_path = content_map[esp]
        section = get_section_name(str(mod_path))
        mod_name = get_mod_name(str(mod_path), section)
        base_path = next((d for d in data_dirs if str(mod_path).startswith(d)), str(mod_path))

        entry = ModEntry(mod_name=mod_name, content_files=[esp], paths_used=[base_path])
        sections.setdefault(section, ModSection(section)).add_or_merge_entry(entry)

    # Track texture-only mods
    for data_dir in data_dirs:
        section = get_section_name(data_dir)
        mod_name = get_mod_name(data_dir, section)
        entry = ModEntry(mod_name=mod_name, content_files=[], paths_used=[data_dir])
        sections.setdefault(section, ModSection(section)).add_or_merge_entry(entry)

    return sections


def write_sections_to_file(sections: Dict[str, ModSection], path: Path):
    lines = []
    for section_name in sorted(sections.keys()):
        section = sections[section_name]
        lines.append(f"## {section_name}")
        lines.append("| Mod Name | Notes | Content File(s) | Paths Used |")
        lines.append("|----------|-------|------------------|-------------|")
        for entry in section.sorted_entries():
            content = ", ".join(entry.content_files)
            paths = ", ".join(entry.paths_used)
            lines.append(f"| {entry.mod_name} | {entry.notes} | {content} | {paths} |")
        lines.append("")
    path.write_text("\n".join(lines))


def load_readme_sections(path: Path) -> Dict[str, ModSection]:
    sections = {}
    section_name = None

    section_pattern = re.compile(r"^## (.+)")
    row_pattern = re.compile(r"^\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|")

    with open(path, "r") as f:
        for line in f:
            section_match = section_pattern.match(line)
            row_match = row_pattern.match(line)

            if section_match:
                section_name = section_match.group(1)
                if section_name not in sections:
                    sections[section_name] = ModSection(name=section_name)
            elif row_match and section_name:
                mod_name, notes, content_files, paths_used = [x.strip() for x in row_match.groups()]

                if mod_name.lower() == "mod name" or mod_name.startswith("---"):
                    continue

                entry = ModEntry(
                    mod_name=mod_name,
                    notes=notes,
                    content_files=[x.strip() for x in content_files.split(",") if x.strip()],
                    paths_used=[x.strip() for x in paths_used.split(",") if x.strip()]
                )
                sections[section_name].add_or_merge_entry(entry)

    return sections


def merge_sections(existing: Dict[str, ModSection], generated: Dict[str, ModSection]) -> Dict[str, ModSection]:
    merged = {}

    for section_name in set(existing.keys()).union(generated.keys()):
        merged_section = ModSection(section_name)

        existing_section = existing.get(section_name, ModSection(section_name))
        generated_section = generated.get(section_name, ModSection(section_name))

        # First, add all entries from README
        for entry in existing_section.entries.values():
            merged_section.add_or_merge_entry(entry)

        # Then, add entries from GENERATED only if their content files aren't already covered
        existing_content_files = {
            cf for e in existing_section.entries.values() for cf in e.content_files
        }

        for entry in generated_section.entries.values():
            if any(cf in existing_content_files for cf in entry.content_files):
                continue  # Skip: already exists in README
            merged_section.add_or_merge_entry(entry)

        merged[section_name] = merged_section

    return merged


def main():
    shutil.copy(OPENMW_CFG, LOCAL_CFG_COPY)
    print(f"Copied {OPENMW_CFG} to {LOCAL_CFG_COPY}")

    data_dirs, content_files = parse_openmw_cfg(OPENMW_CFG)
    content_map = find_content_paths(data_dirs)

    generated = generate_mod_sections(data_dirs, content_files, content_map)
    write_sections_to_file(generated, GENERATED_PATH)

    if README_PATH.exists():
        existing = load_readme_sections(README_PATH)
        merged = merge_sections(existing, generated)
        write_sections_to_file(merged, MERGED_PATH)
        print(f"Generated {MERGED_PATH}")
    else:
        print("README.md not found; only GENERATED.md created.")


if __name__ == "__main__":
    main()
