from classes import ModDictionary
import os, sys

MARKDOWN_PATH = "README.md"

def add_missing_mods(config_dict, result_dict):
    for section_name, source_section in config_dict.sections.items():
        if section_name not in result_dict.sections:
            result_dict.sections[section_name] = source_section
            continue  # Entire section added

        target_section = result_dict.sections[section_name]

        for source_mod in source_section.mods:
            # Check if mod already exists in target section
            target_mod = next((m for m in target_section.mods if m.name == source_mod.name), None)

            if not target_mod:
                # Entire mod is missing, add it
                target_section.mods.append(source_mod)
                continue

            # Add missing files
            for source_file in source_mod.files:
                if not any(f.file == source_file.file for f in target_mod.files):
                    target_mod.files.append(source_file)

            # Add missing paths
            for source_path in source_mod.paths:
                if not any(p.path == source_path.path for p in target_mod.paths):
                    target_mod.paths.append(source_path)


def remove_deleted_mods(config_dict, result_dict):
    # Remove entire sections that no longer exist
    to_delete_sections = [
        section_name for section_name in result_dict.sections
        if section_name not in config_dict.sections
    ]
    for section_name in to_delete_sections:
        del result_dict.sections[section_name]

    # For remaining sections, clean up individual mods and their contents
    for section_name, result_section in result_dict.sections.items():
        if section_name not in config_dict.sections:
            continue

        source_section = config_dict.sections[section_name]

        source_mods_by_name = {mod.name: mod for mod in source_section.mods}

        updated_mods = []
        for result_mod in result_section.mods:
            source_mod = source_mods_by_name.get(result_mod.name)
            if not source_mod:
                continue  # Mod no longer exists

            # Remove deleted files
            result_mod.files = [
                f for f in result_mod.files
                if any(f.file == s.file for s in source_mod.files)
            ]

            # Remove deleted paths
            result_mod.paths = [
                p for p in result_mod.paths
                if any(p.path == s.path for s in source_mod.paths)
            ]

            updated_mods.append(result_mod)

        result_section.mods = updated_mods


def main():
    if not os.path.exists(MARKDOWN_PATH):
        print(f"❌ {MARKDOWN_PATH} not found.")
        return

    print("📥 Loading config and markdown...")
    config_dict = ModDictionary(from_markdown=False)
    result_dict = ModDictionary(from_markdown=True)

    print("🔁 Merging...")
    add_missing_mods(config_dict, result_dict)
    remove_deleted_mods(config_dict, result_dict)

    print("💾 Saving merged result to markdown...")
    result_dict.generate_markdown(MARKDOWN_PATH)
    print(f"✅ Saved to {MARKDOWN_PATH}")

if __name__ == "__main__":
    main()
