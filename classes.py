import re
from pathlib import Path

MOD_DIR = "/home/chris/mods/morrowind/"
OPENMW_CFG = "openmw.cfg"
MARKDOWN_OUTPUT = "README.md"

class Mod:
    def __init__(self, name: str):
        self.name = name
        self.files = []
        self.paths = []
        self.notes = ''
        self.url = ''

    def __str__(self):
        files_str = "\n".join(str(c) for c in self.files)
        paths_str = "\n".join(str(d) for d in self.paths)
        return (f"{self.name}\n"
                f"    Files:\n" + '\n'.join([f"  {path}" for path in files_str.splitlines()] or ['\t\t(none)']) + '\n'
                f"    Paths:\n" + '\n'.join([f"  {path}" for path in paths_str.splitlines()] or ['\t\t(none)']))

    def add_file(self, files: 'ModContentFile'):
        if not any(content.name == files.name and content.file == files.file for content in self.files):
            self.files.append(files)

    def add_path(self, paths: 'ModPath'):
        if not any(modpath.name == paths.name and modpath.path == paths.path for modpath in self.paths):
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

        # if isinstance(mod_entry, ModContentFile):
        #     mod_name = mod_entry.get_mod_name()

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
        return (f"{self.name}\n"
                f"{'~'*60}\n"
                f"{mods_str or '  No mods in this section.'}\n"
                f"{'~'*60}")


class ModDictionary:
    def __init__(self, from_markdown: bool = False):
        if from_markdown:
            self.sections = self.read_markdown(MARKDOWN_OUTPUT)
        else:
            self.sections = self.read_config(OPENMW_CFG)

    def read_markdown(self, markdown_path: str) -> dict[str, ModSection]:
        sections = {}
        current_section = None
        table_pattern = re.compile(r'^\| (.+?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$')

        with open(markdown_path, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line.startswith('|---') or line.startswith('| Name'):
                continue

            if line.startswith('## '):
                section_name = line.replace('## ', '').strip()
                current_section = ModSection(section_name, "")
                sections[section_name] = current_section
            elif table_pattern.match(line):
                match = table_pattern.match(line)
                name, notes, url, files_str, paths_str = [part.strip() for part in match.groups()]

                # print(name)
                # print(match)

                mod = Mod(name)
                mod.notes = notes
                mod.url = url

                if files_str and files_str.lower() != "(none)":
                    for file_path in [f.strip() for f in files_str.split(',')]:
                        if file_path:
                            mod.add_file(ModContentFile(name, file_path))

                if paths_str and paths_str.lower() != "(none)":
                    for path in [p.strip() for p in paths_str.split(',')]:
                        if path:
                            mod.add_path(ModPath(name, path))

                if current_section:
                    current_section.mods.append(mod)

        return sections

    def generate_markdown(self, output_path):
        """
        Generates the GENERATED.md file from the mod sections and their content.
        Each section will be a header with a table for mods.
        Paths will be newline-separated in the table.
        """
        with open(output_path, "w") as output_file:
            for section in sorted(self.sections.values(), key=lambda x: x.name):
                # Write section header
                output_file.write(f"## {section.name}\n\n")
                
                # Write table header
                output_file.write("| Name | Notes | URL   | Files | Paths |\n")
                output_file.write("|------|-------|-------|-------|-------|\n")

                # Iterate over mods in the section and write a row for each
                for mod in section.mods:
                    # Convert files and paths to newline-separated strings
                    files_str = "\n".join(str(f) for f in mod.files) if mod.files else "(none)"
                    paths_str = "\n".join(str(p) for p in mod.paths) if mod.paths else "(none)"
                    
                    files_str = files_str.replace(' ', '').replace('\n', ', ')
                    paths_str = paths_str.replace(' ', '').replace('\n', ', ')
                    
                    line = f"| {mod.name} | {mod.notes} | {mod.url} | {files_str} | {paths_str} |\n"
                    # print(line)

                    # Write mod details in the table row format
                    output_file.write(line)

                output_file.write("\n")  # Blank line between sections

        print(f"Generated {output_path} successfully.")

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
                print(line, end='')

                # skip base game + expansions (not "mods" but requires)
                if (line == "content=Tribunal.esm" or 
                    line == "content=Bloodmoon.esm" or 
                    line == "content=Morrowind.esm" or 
                    line.startswith("#") or 
                    line == "" or 
                    line.endswith("Morrowind/Data Files\"") or
                    not (line.startswith('data=') or line.startswith('content='))):
                    print('')
                    continue

                line = line.replace(MOD_DIR, "")
                isContent = 'content=' in line
                section = ""
                path = ""
                name = ""

                if isContent:
                    path = self.find_mod_file(line.split('=')[-1] , MOD_DIR)

                    if path is None:
                        continue
    
                    section = self.get_section(path)

                    if path.count('/') == 1: # if in root
                        name = section       # use section name as mod name
                    else:
                        parts = path.split('/')

                        name = parts[1] if len(parts) > 1 else parts[0]

                    mod_entry = ModContentFile(name, path)
                else:
                    parts = line.split('/')
                    name = (parts[1] if len(parts) > 1 else parts[-1]).replace('"','').replace('data=','')
                    path = line.split('=')[-1].replace('"','')

                    mod_entry = ModPath(name, path)
                    section = self.get_section(path)

                print('  ✅')
                
                print(f'  Section:\t{section}')
                print(f'  Name:\t\t{name}')
                print(f'  Path:\t\t{path}')
                print(f'  isContent:\t{isContent}')
                print('---')

                # Ensure section exists
                if section not in sections:
                    sections[section] = ModSection(section, path)

                # Add the mod entry
                sections[section].add_mod(mod_entry)

        return sections