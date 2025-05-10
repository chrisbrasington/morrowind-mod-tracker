from classes import ModDictionary

GENERATED_MARKDOWN = "README.md"

def main():
    print("🔗 Loading mods from markdown...")

    # Load mods from GENERATED.md
    mod_dict = ModDictionary(from_markdown=True)

    print(f"\nLoaded {len(mod_dict.sections)} sections.\n")

    # Print out all mods for verification
    for name, section in mod_dict.sections.items():
        print(section)

if __name__ == "__main__":
    main()
