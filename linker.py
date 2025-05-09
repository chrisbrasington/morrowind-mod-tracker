import re
import argparse
from pathlib import Path
from collections import defaultdict

README_PATH = Path("README.md")

def extract_mod_data():
    mod_data = {}
    content_files = defaultdict(list)
    paths_used = defaultdict(set)

    row_pattern = re.compile(r"\| (.+?) \| (.*?) \| (.+?) \| (.+?) \|")

    with open(README_PATH, "r") as f:
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
            if plain_name not in mod_data and mod_name_cell != "Mod Name":
                mod_data[plain_name] = {"linked": mod_name_cell, "url": url, "notes": notes.strip()}

            content_files[plain_name].append(content_file.strip())
            paths_used[plain_name].add(paths.strip())

    return mod_data, content_files, paths_used

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

def print_mod_info(mod_name, data, content_files, paths_used):
    print(f"\n🔹 {mod_name}")
    if content_files.get(mod_name):
        print("  Content Files:")
        for cf in content_files[mod_name]:
            print(f"    - {cf}")
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

def interactive_walk(skip_existing):
    mod_data, content_files, paths_used = extract_mod_data()
    last_url = ""
    last_notes = ""

    for i, (mod_name, data) in enumerate(sorted(mod_data.items()), 1):
        print_mod_info(mod_name, data, content_files, paths_used)

        # Check if we should skip this mod (i.e., it already has a URL set)
        if skip_existing and data["url"]:
            print(f"  ✅ Skipping {mod_name} (URL already set: {data['url']})")
            continue

        url = input("  Enter new URL (or press Enter to skip, 'ditto' to reuse last): ").strip()
        if url.lower() == "ditto":
            url = last_url
        elif url:
            last_url = url

        if not url:
            continue  # Skip this mod if no URL is provided

        notes = input("  Enter notes (or press Enter to leave unchanged, 'ditto' to reuse last): ").strip()
        if notes.lower() == "ditto":
            notes = last_notes
        elif notes:
            last_notes = notes

        update_readme_with_link(mod_name, url, notes)
        print(f"  ✅ Updated {mod_name}.")

def interactive_single():
    mod_data, content_files, paths_used = extract_mod_data()

    print("Select a mod to update:")
    for i, name in enumerate(sorted(mod_data.keys()), 1):
        print(f"{i} - {name}")

    try:
        mod_index = int(input("Enter the number of the mod: ")) - 1
        mod_name = sorted(mod_data.keys())[mod_index]
    except (IndexError, ValueError):
        print("Invalid selection.")
        return

    data = mod_data[mod_name]
    print_mod_info(mod_name, data, content_files, paths_used)

    url = input("  Enter new URL (or press Enter to skip): ").strip()
    notes = input("  Enter notes (or press Enter to leave unchanged): ").strip()
    update_readme_with_link(mod_name, url, notes)
    print(f"  ✅ Updated {mod_name}.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--walk", action="store_true", help="Walk through each mod interactively")
    parser.add_argument("-s", "--skip", action="store_true", help="Skip mods that already have a URL")
    args = parser.parse_args()

    if args.walk:
        interactive_walk(args.skip)
    else:
        interactive_single()

if __name__ == "__main__":
    main()
