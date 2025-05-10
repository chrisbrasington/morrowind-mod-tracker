import argparse
from mod_data import ModData

README_PATH = "README.md"

def print_section_mods(mod_data, content_files, paths_used, section_name):
    print(f"\n🔹 {section_name}")
    mods_in_section = [mod for mod in mod_data if mod.startswith(section_name)]
    
    if not mods_in_section:
        print("  No mods found in this section.")
        return

    for i, mod_name in enumerate(mods_in_section, 1):
        print(f"{i} - {mod_name}")

    try:
        mod_index = int(input("Enter the number of the mod: ")) - 1
        mod_name = mods_in_section[mod_index]
    except (IndexError, ValueError):
        print("Invalid selection.")
        return

    data = mod_data[mod_name]
    print_mod_info(mod_name, data, content_files, paths_used)

    url = input("  Enter new URL (or press Enter to skip): ").strip()
    notes = input("  Enter notes (or press Enter to leave unchanged): ").strip()
    mod_data.update_readme_with_link(README_PATH, mod_name, url, notes)
    print(f"  ✅ Updated {mod_name}.")

def print_mod_info(mod_name, data, content_files, paths_used):
    print(f"\n🔹 {mod_name}")
    if content_files.get(mod_name):
        print("  Content Files:")
        for cf in content_files[mod_name]:
            print(f"    - {cf}" if cf else "    - No content files")
    if paths_used.get(mod_name):
        print("  Paths Used:")
        for p in sorted(paths_used[mod_name]):
            print(f"    - {p}")

    if data["url"]:
        print(f"  Current URL: {data['url']}")
    else:
        print("  No URL found.")

    if data["notes"]:
        print(f"  Notes: {data['notes']}")
    else:
        print("  No notes found.")

def interactive_walk():
    mod_data_handler = ModData()
    mod_data_handler.extract_data_from_readme(README_PATH)
    mod_data, content_files, paths_used = mod_data_handler.get_mod_data()

    section_names = sorted(set([mod.split(" ")[0] for mod in mod_data.keys()]))

    for section_name in section_names:
        print_section_mods(mod_data, content_files, paths_used, section_name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--walk", action="store_true", help="Walk through each mod interactively")
    args = parser.parse_args()

    if args.walk:
        interactive_walk()

if __name__ == "__main__":
    main()
