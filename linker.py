import argparse
import os
from classes import ModDictionary

MARKDOWN_PATH = "README.md"

def flatten_mods(mod_dict):
    """Return a list of (section_name, mod) tuples."""
    all_mods = []
    for section_name, section in mod_dict.sections.items():
        for mod in section.mods:
            all_mods.append((section_name, mod))
    return all_mods

def display_mod_list(mods):
    for idx, (section_name, mod) in enumerate(mods, 1):
        url_display = mod.url if mod.url else "(no url)"
        notes_display = mod.notes if mod.notes else "(no notes)"
        print(f"{idx}. [{section_name}] {mod.name}\n     URL: {url_display}\n     Notes: {notes_display}")

def edit_mod(mod):
    print(f"\nEditing '{mod.name}'")

    url = input(f"  Current URL: {mod.url or '(none)'}\n  New URL (or Enter to skip): ").strip()
    notes = input(f"  Current Notes: {mod.notes or '(none)'}\n  New Notes (or Enter to skip): ").strip()

    if url:
        mod.url = url
    if notes:
        mod.notes = notes

    print("  ✅ Mod updated.\n")

def interactive_selection(mod_dict):
    while True:
        mods = flatten_mods(mod_dict)
        display_mod_list(mods)

        choice = input("\nEnter a number to edit a mod (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            break

        if not choice.isdigit() or not (1 <= int(choice) <= len(mods)):
            break

        _, mod = mods[int(choice) - 1]
        edit_mod(mod)

        save(mod_dict)

def save(mod_dict):
    # Save updated markdown
    print("💾 Saving updated markdown...")
    mod_dict.generate_markdown(MARKDOWN_PATH)
    print(f"✅ Saved to {MARKDOWN_PATH}.")

def walk_missing_urls(mod_dict):
    mods = flatten_mods(mod_dict)
    for section_name, mod in mods:
        if not mod.url:
            print(f"\n[{section_name}] {mod.name}")
            edit_mod(mod)
            save(mod_dict)

def main():
    parser = argparse.ArgumentParser(description="Mod Linker Utility")
    parser.add_argument('-w', '--walk', action='store_true', help="Walk through mods missing a URL")
    args = parser.parse_args()

    if not os.path.exists(MARKDOWN_PATH):
        print(f"❌ {MARKDOWN_PATH} not found.")
        return

    mod_dict = ModDictionary(from_markdown=True)

    if args.walk:
        walk_missing_urls(mod_dict)
    else:
        interactive_selection(mod_dict)

    # Save updated markdown
    save(mod_dict)

if __name__ == "__main__":
    main()
