import sys
from pathlib import Path

# OPENMW_CFG = Path.home() / ".config/openmw/openmw.cfg"
MOD_DIR = "/home/chris/mods/morrowind/"
OPENMW_CFG = "openmw.cfg"

class Mod:
    def __init__(self, name: str):
        self.name = name

class ModData:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path.replace(MOD_DIR, '')

    def __str__(self):
        return f"    {self.name}\n    Path: [{self.path}]"


class ModContent:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path.replace(MOD_DIR, '')

    def __str__(self):
        return f"    {self.name}\n    Path: [{self.path}]"


class ModSection:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.content = []
        self.data = []

    def add_content(self, content: ModContent):
        if not any(c.name == content.name for c in self.content):
            self.content.append(content)

    def add_data(self, data: ModData):
        if not any(d.name == data.name for d in self.data):
            self.data.append(data)

    def __str__(self):
        content_str = "\n".join(str(c) for c in self.content)
        data_str = "\n".join(str(d) for d in self.data)
        return (f"ModSection: {self.name}\n"
                f"  Content:\n{content_str or '    (none)'}\n"
                f"  Data:\n{data_str or '    (none)'}\n"
                f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

class ModDictionary:
    def __init__(self):
        self.sections = self.read_config(OPENMW_CFG)  # Store sections as a dictionary or list

    def find_mod_file(self, name, base_dir):
        base_path = Path(base_dir)
        for match in base_path.rglob(name):  
            return str(match)  
        return None 

    def get_section(self, path):
        path = path.split('=')[-1].replace('"','')

        return path.replace(MOD_DIR, '').split('/')[0]

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

                if isContent:
                    name = line.split('=')[-1]
                    path = self.find_mod_file(name, MOD_DIR)
                    section = self.get_section(path)

                else: # is data
                    parts = line.split('/')
                    section = self.get_section(line)
                    name = '/'.join(parts[1:]).replace('"','')
                    path = line.split('=')[-1].replace('"','')

                # if section does not exist, add it
                if section not in sections:
                    sections[section] = ModSection(section, path)

                if isContent:
                    sections[section].add_content(ModContent(name, path))
                else:
                    sections[section].add_data(ModData(name, path))
 
                
        return sections

def main():
    mod_dict = ModDictionary()
    for name, section in mod_dict.sections.items():
        print(section)

if __name__ == "__main__":
    main()
