import sys

from classes import ModDictionary

def main():
    mod_dict = ModDictionary()
    mod_dict.sections = dict(sorted(mod_dict.sections.items()))
    print(f"{'~'*60}")
    for name, section in mod_dict.sections.items():
        print(section)

    mod_dict.generate_markdown("GENERATED.md")

if __name__ == "__main__":
    main()
