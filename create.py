import sys
from pathlib import Path

# OPENMW_CFG = Path.home() / ".config/openmw/openmw.cfg"
MOD_DIR = "/home/chris/mods/morrowind/"
OPENMW_CFG = "openmw.cfg"

class Mod:
    def __init__(self, name: str):
        self.name = name
        self.files = []
        self.paths = []

    def __str__(self):
        files_str = "\n".join(str(c) for c in self.files)
        paths_str = "\n".join(str(d) for d in self.paths)
        return (f"\tMod:\n\t      {self.name}\n"
                f"\tFiles:\n\t{files_str or '(none)'}\n"
                f"\tPaths:\n" + '\n'.join([f"\t{path}" for path in paths_str.splitlines()] or ['\t\t(none)']))


    def add_file(self, files: 'ModfilesFile'):
        if not any(c.name == files.name and c.path == files.path for c in self.files):
            self.files.append(files)

    def add_path(self, paths: 'ModPath'):
        if not any(d.name == paths.name and d.path == paths.path for d in self.paths):
            self.paths.append(paths)

class ModPath:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path.replace(MOD_DIR, '')

    def __str__(self):
        return f"      {self.path}"


class ModContentFile:
    def __init__(self, name: str, path: str):
        self.name = name
        self.file = path.replace(MOD_DIR, '')

    def get_mod_name(self):
        parts = self.file.split('/')
        return parts[1] if len(parts) > 1  else self.file

    def __str__(self):
        return f"      {self.file}"


class ModSection:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.mods = []

    def add_mod(self, mod_entry: ModPath | ModContentFile):
        # Determine the mod name
        mod_name = mod_entry.name

        if isinstance(mod_entry, ModContentFile):
            mod_name = mod_entry.get_mod_name()

        # Try to find existing mod
        mod = next((m for m in self.mods if m.name == mod_name), None)
        if not mod:
            mod = Mod(mod_name)
            self.mods.append(mod)

        # Add content or data to the correct field, avoid duplicates
        if isinstance(mod_entry, ModContentFile):
            mod.add_file(mod_entry)
        elif isinstance(mod_entry, ModPath):
            mod.add_path(mod_entry)

    def __str__(self):
        mods_str = "\n".join(str(m) for m in self.mods)
        return (f"Section: {self.name}\n"
                f"{mods_str or '  No mods in this section.'}\n"
                f"{'~'*60}")


class ModDictionary:
    def __init__(self):
        self.sections = self.read_config(OPENMW_CFG)  # Store sections as a dictionary or list

    def get_section(self, path):
        parts = path.split('/')
        return parts[0]

    def find_mod_file(self, name, base_dir):
        base_path = Path(base_dir)
        for match in base_path.rglob(name):  
            return str(match).replace(MOD_DIR, '')
        return None 

    def read_config(self, config_path):
        sections = {}
        with open(config_path, "r") as file:
            for line in file:
                line = line.strip()

                if line.startswith("#") or line == "":
                    continue

                line = line.replace(MOD_DIR, "")
                isContent = 'content=' in line
                section = ""
                path = ""
                name = ""

                if isContent:
                    name = line.split('=')[-1]  
                    path = self.find_mod_file(name, MOD_DIR)

                    mod_entry = ModContentFile(name, path)
                    section = self.get_section(path)
                else:
                    parts = line.split('/')
                    name = (parts[1] if len(parts) > 1 else parts[-1]).replace('"','')
                    path = line.split('=')[-1].replace('"','')

                    mod_entry = ModPath(name, path)
                    section = self.get_section(path)

                # print(line)
                # print(f'  Section:\t{section}')
                # print(f'  Name:\t\t{name}')
                # print(f'  Path:\t\t{path}')
                # print(f'  isContent:\t{isContent}')
                # print('---')


                # Ensure section exists
                if section not in sections:
                    sections[section] = ModSection(section, path)

                # Add the mod entry
                sections[section].add_mod(mod_entry)

        return sections


def main():
    mod_dict = ModDictionary()
    print(f"{'~'*60}")
    for name, section in mod_dict.sections.items():
        print(section)

if __name__ == "__main__":
    main()
