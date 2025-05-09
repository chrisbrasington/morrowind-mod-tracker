import re
import argparse
from pathlib import Path

README_PATH = Path("README.md")

def extract_mod_data():
    mod_data = {}  # {plain_mod_name: (linked_mod_name, notes)}

    row_pattern = re.compile(r"\| (.+?) \| (.*?) \| .+? \| .+? \|")

    with open(README_PATH, "r") as f:
        for line in f:
            row_match = row_pattern.match(line)
            if row_match:
                mod_name_cell, notes = row_match.groups()
                match = re.match(r"\[(.+?)\]\((.+?)\)", mod_name_cell)
                if match:
                    plain_name = match.group(1)
                    url = match.group(2)
                else:
                    plain_name = mod_name_cell
                    url = None
                mod_data[plain_name] = {"linked": mod_name_cell, "url": url, "notes": notes.strip()}
    return mod_data

def update_readme_with_link(mod_name, url, notes):
    row_pattern = re.compile(r"\| (.+?) \| (.*?) \| (.+?) \| (.+?) \|")

    with open(README_PATH, "r") as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        row_match = row_pattern.match(line)
        if row_match:
            mod_name_cell, existing_notes, content_file, paths_used = row_match.groups()
            plain_name = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1", mod_name_cell)

            if plain_name == mod_name:
                linked_name = f"[{plain_name}]({url})" if url else mod_name_cell
                notes = notes or existing_notes
                updated_lines.append(f"| {linked_name} | {notes} | {content_file} | {paths_used} |\n")
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)

    with open(README_PATH, "w") as f:
        f.writelines(updated_lines)

def interactive_walk():
    mod_data = extract_mod_data()

    for i, (mod_name, data) in enumerate(sorted(mod_data.items()), 1):
        print(f"\n{i}. {mod_name}")
        if data["url"]:
            print(f"  Current URL: {data['url']}")
        else:
            print("  No URL found.")

        if data["notes"]:
            print(f"  Notes: {data['notes']}")
        else:
            print("  No notes found.")

        url = input("  Enter new URL (or press Enter to skip): ").strip()
        if not url:
            continue
        notes = input("  Enter notes (or press Enter to leave unchanged): ").strip()
        update_readme_with_link(mod_name, url, notes)
        print(f"  → Updated {mod_name}.")

def interactive_single():
    mod_data = extract_mod_data()

    print("Select a mod to update:")
    for i, name in enumerate(sorted(mod_data.keys()), 1):
        print(f"{i} - {name}")

    try:
        mod_index = int(input("Enter the number of the mod: ")) - 1
        mod_name = sorted(mod_data.keys())[mod_index]
    except (IndexError, ValueError):
        print("Invalid selection.")
        return

    url = input(f"Enter the URL for {mod_name}: ").strip()
    notes = input(f"Enter notes for {mod_name} (or hit Enter to skip): ").strip()

    update_readme_with_link(mod_name, url, notes)
    print(f"Updated {mod_name} with link and notes.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--walk", action="store_true", help="Walk through each mod interactively")
    args = parser.parse_args()

    if args.walk:
        interactive_walk()
    else:
        interactive_single()

if __name__ == "__main__":
    main()
