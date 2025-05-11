# from classes import ModDictionary
# import os

# MARKDOWN_PATH = "README.md"

# def flatten_mods(mod_dict):
#     """Return a dict mapping mod name to (section_name, mod)."""
#     flat = {}
#     for section_name, section in mod_dict.sections.items():
#         # Ensure that section is a ModSection instance
#         if isinstance(section, ModSection):  # Check that section is an instance of ModSection
#             for mod in section.mods:  # Access the 'mods' attribute correctly
#                 flat[mod.name] = (section_name, mod)
#     return flat

# def add_missing_mods(config_dict, result_dict):
#     config_flat = flatten_mods(config_dict)
#     result_flat = flatten_mods(result_dict)

#     for mod_name, (section_name, mod) in config_flat.items():
#         if mod_name not in result_flat:
#             print(f"➕ Adding missing mod: '{mod_name}' to section '{section_name}'")
            
#             # Add the mod to the appropriate section in the result_dict
#             if section_name not in result_dict.sections:
#                 result_dict.sections[section_name] = []  # Create new section if it doesn't exist
#             result_dict.sections[section_name].append(mod)

# def remove_deleted_mods(config_dict, result_dict):
#     config_flat = flatten_mods(config_dict)
#     result_flat = flatten_mods(result_dict)

#     for mod_name, (section_name, mod) in result_flat.items():
#         if mod_name not in config_flat:
#             prompt = input(f"❓ Mod '{mod_name}' exists in markdown but not in config. Delete? [y/N]: ").strip().lower()
#             if prompt == 'y':
#                 # Remove the mod from the appropriate section in result_dict
#                 result_dict.sections[section_name].remove(mod)
#                 print(f"🗑️ Deleted '{mod_name}'")

# def main():
#     if not os.path.exists(MARKDOWN_PATH):
#         print(f"❌ {MARKDOWN_PATH} not found.")
#         return

#     print("📥 Loading config and markdown...")
#     config_dict = ModDictionary(from_markdown=False)
#     result_dict = ModDictionary(from_markdown=True)

#     print("🔁 Merging...")
#     add_missing_mods(config_dict, result_dict)
#     remove_deleted_mods(config_dict, result_dict)

#     print("💾 Saving merged result to markdown...")
#     result_dict.generate_markdown(MARKDOWN_PATH)
#     print(f"✅ Saved to {MARKDOWN_PATH}")

# if __name__ == "__main__":
#     main()
