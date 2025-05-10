import os
import re
import shutil
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict

# Config paths
OPENMW_CFG = Path.home() / ".config/openmw/openmw.cfg"
LOCAL_CFG_COPY = Path("./openmw.cfg")
README_PATH = Path("README.md")
GENERATED_MD = Path("GENERATED.md")
MERGED_MD = Path("MERGED.md")


@dataclass
class ModEntry:
    mod_name: str
    notes: str = ""
    content_files: List[str] = field(default_factory=list)
    paths_used: List[str] = field(default_factory=list)

    def merge(self, other: 'ModEntry'):
        self.content_files = sorted(set(self.content_files + other.content_files))
        self.paths_used = sorted(set(self.paths_used + other.paths_used))


@dataclass
class ModSection:
    name: str
    entries: List[ModEntry] = field(default_factory=list)

    def find_entry_by_content_file(self, content_file: str) -> ModEntry:
        for entry in self.entries:
            if content_file in entry.content_files:
                return entry
        return None

    def add_or_merge_entry(self, new_entry: ModEntry):
        existing = self.find_entry_by_content_file(new_entry.content_files[0])
        if existing:
            existing.merge(new_entry)
        else:
            self.entries.append(new_entry)


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


def find_content_paths(data_dirs: List[str]):
    content_map = {}
    for base_dir in data_dirs:
        for root, _, files in os.walk(base_dir):
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


def generate_sections(data_dirs, content_files, content_map) -> Dict[str, ModSection]:
    sections = {}

    for esp in content_files:
        if esp not in content_map:
            print(f"[WARN] Could not find ESP on disk: {esp}")
            continue

        mod_path = content_map[esp]
        section = get_section_name(str(mod_path))
        mod_name = Path(mod_path).name
        matched_path = ""

        for base in data_dirs:
            if str(mod_path).startswith(base):
                matched_path = base
                break

        if section not in sections:
            sections[section] = ModSection(name=section)

        entry = ModEntry(
            mod_name=mod_name,
            content_files=[esp],
            paths_used=[matched_path or str(mod_path)]
        )
        sections[section].add_or_merge_entry(entry)

    return sections


def write_markdown(sections: Dict[str, ModSection], path: Path):
    lines = []

    for section in sorted(sections.keys()):
        mod_section = sections[section]
        if not mod_section.entries:
            continue

        lines.append(f"## {section}\n")
        lines.append("| Mod Name | Notes | Content File(s) | Paths Used |")
        lines.append("|----------|-------|------------------|-------------|")

        for entry in sorted(mod_section.entries, key=lambda e: e.mod_name.lower()):
            content = ", ".join(sorted(entry.content_files))
            paths = ", ".join(sorted(entry.paths_used))
            lines.append(f"| {entry.mod_name} | {entry.notes} | {content} | {paths} |")
        lines.append("")  # Blank line after each section

    path.write_text("\n".join(lines))
    print(f"[INFO] Wrote markdown to {path}")


def load_readme_sections(path: Path) -> Dict[str, ModSection]:
    sections = {}
    section_name = None

    section_pattern = re.compile(r"^## (.+)")
    row_pattern = re.compile(r"^\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|")

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

                # ✅ Skip table headers or separator lines
                if mod_name.lower() == "mod name" or mod_name.startswith("---"):
                    continue

                entry = ModEntry(
                    mod_name=mod_name,
                    notes=notes,
                    content_files=[x.strip() for x in content_files.split(",")],
                    paths_used=[x.strip() for x in paths_used.split(",")]
                )
                sections[section_name].add_or_merge_entry(entry)

    return sections

def merge_sections(existing: Dict[str, ModSection], generated: Dict[str, ModSection]) -> Dict[str, ModSection]:
    merged = {name: ModSection(name=name, entries=list(sec.entries)) for name, sec in existing.items()}

    for section, gen_sec in generated.items():
        if section not in merged:
            merged[section] = ModSection(name=section)

        for entry in gen_sec.entries:
            duplicate = any(
                entry.content_files[0] in existing_entry.content_files
                for existing_entry in merged[section].entries
            )
            if not duplicate:
                merged[section].add_or_merge_entry(entry)

    return merged


def main():
    # Backup original config
    shutil.copy(OPENMW_CFG, LOCAL_CFG_COPY)
    print(f"[INFO] Copied {OPENMW_CFG} to {LOCAL_CFG_COPY}")

    # Parse config and find data
    data_dirs, content_files = parse_openmw_cfg(OPENMW_CFG)
    content_map = find_content_paths(data_dirs)
    generated_sections = generate_sections(data_dirs, content_files, content_map)

    # Write GENERATED.md
    write_markdown(generated_sections, GENERATED_MD)

    # Load README.md
    if README_PATH.exists():
        existing_sections = load_readme_sections(README_PATH)
    else:
        existing_sections = {}

    # Merge and write MERGED.md
    merged_sections = merge_sections(existing_sections, generated_sections)
    write_markdown(merged_sections, MERGED_MD)


if __name__ == "__main__":
    main()
