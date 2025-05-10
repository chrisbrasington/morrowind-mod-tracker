import re
from collections import defaultdict
from typing import List, Dict


class ModEntry:
    def __init__(self, mod_name: str, content_files: List[str] = None, paths_used: List[str] = None, notes: str = ""):
        self.mod_name = mod_name
        self.content_files = content_files or []
        self.paths_used = paths_used or []
        self.notes = notes

    def add_or_merge(self, other):
        if other.mod_name == self.mod_name:
            # Merge content files and paths
            self.content_files.extend([cf for cf in other.content_files if cf not in self.content_files])
            self.paths_used.extend([path for path in other.paths_used if path not in self.paths_used])


class ModSection:
    def __init__(self, name: str):
        self.name = name
        self.entries: Dict[str, ModEntry] = {}

    def add_or_merge_entry(self, entry: ModEntry):
        if entry.mod_name not in self.entries:
            self.entries[entry.mod_name] = entry
        else:
            self.entries[entry.mod_name].add_or_merge(entry)

    def sorted_entries(self):
        return sorted(self.entries.values(), key=lambda e: e.mod_name)


class ModData:
    def __init__(self):
        self.mod_data = {}
        self.content_files = defaultdict(list)
        self.paths_used = defaultdict(set)
        self.sections: Dict[str, ModSection] = {}

    def extract_data_from_readme(self, readme_path):
        row_pattern = re.compile(r"\| (.+?) \| (.*?) \| (.+?) \| (.+?) \|")

        with open(readme_path, "r") as f:
            for line in f:
                match = row_pattern.match(line)
                if not match:
                    continue
                mod_name_cell, notes, content_file, paths = match.groups()

                # Extract plain mod name and url
                match_link = re.match(r"\[(.+?)\]\((.+?)\)", mod_name_cell)
                if match_link:
                    plain_name = match_link.group(1)
                    url = match_link.group(2)
                else:
                    plain_name = mod_name_cell
                    url = None

                # Save mod metadata
                if plain_name not in self.mod_data and mod_name_cell != "Mod Name":
                    self.mod_data[plain_name] = {"linked": mod_name_cell, "url": url, "notes": notes.strip()}

                self.content_files[plain_name].append(content_file.strip() if content_file.strip() else None)
                self.paths_used[plain_name].add(paths.strip())

    def get_mod_data(self):
        return self.mod_data, self.content_files, self.paths_used

    def add_or_merge_entry(self, entry: ModEntry, section_name: str):
        if section_name not in self.sections:
            self.sections[section_name] = ModSection(section_name)
        self.sections[section_name].add_or_merge_entry(entry)

    def get_mod_sections(self):
        return self.sections

    def update_readme_with_link(self, readme_path, mod_name, url, notes):
        row_pattern = re.compile(r"\| (.+?) \| (.*?) \| (.+?) \| (.+?) \|")

        with open(readme_path, "r") as f:
            lines = f.readlines()

        updated_lines = []
        for line in lines:
            row_match = row_pattern.match(line)
            if row_match:
                mod_name_cell, existing_notes, content_file, paths_used = row_match.groups()
                plain_name = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1", mod_name_cell)

                if plain_name == mod_name:
                    linked_name = f"[{plain_name}]({url})" if url and not existing_notes else mod_name_cell
                    notes = notes or existing_notes
                    updated_lines.append(f"| {linked_name} | {notes} | {content_file} | {paths_used} |\n")
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        with open(readme_path, "w") as f:
            f.writelines(updated_lines)
