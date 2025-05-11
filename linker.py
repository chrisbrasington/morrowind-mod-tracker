import argparse
import os, platform, sys, webbrowser
from classes import ModDictionary
#from duckduckgo_search import DDGS
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urlparse, parse_qs

MARKDOWN_PATH = "README.md"

class DuckDuckGoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.first_link = None

    def handle_starttag(self, tag, attrs):
        if tag == "a" and ("class", "result__a") in attrs:
            href = dict(attrs).get("href", "")
            self.links.append(href)

    def get_priority_link(self):
        # Lists for categorized URLs
        modding_openmw_urls = []
        nexusmods_urls = []
        other_urls = []

        for url in self.links:  # Now we're using self.links, which is populated during parsing
            # Parse the DuckDuckGo link
            parsed_url = urlparse(url)
            
            # Extract the 'uddg' query parameter
            query_params = parse_qs(parsed_url.query)
            if 'uddg' in query_params:
                # Decode the URL and append to the appropriate list based on domain
                cleaned_url = query_params['uddg'][0]
                if 'nexusmods.com' in cleaned_url:
                    nexusmods_urls.append(cleaned_url)
                elif 'modding-openmw.com' in cleaned_url:
                    modding_openmw_urls.append(cleaned_url)
                else:
                    other_urls.append(cleaned_url)

        # Concatenate the lists with priority (modding-openmw.com > nexusmods.com > others)
        sorted_urls = modding_openmw_urls + nexusmods_urls + other_urls

        # Group by category for printing
        categorized_links = {
            'nexusmods': nexusmods_urls,
            'open-mw': modding_openmw_urls,
            'other': other_urls
        }

        # Print the categorized URLs
        for category, links in categorized_links.items():
            if links:
                print(f"{category}:")
                for link in links:
                    print(f"  {link}")

        # Return the highest priority link (first modding-openmw.com link, if available)
        return sorted_urls[0] if sorted_urls else None

def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def display_mod_list(mods):
    for idx, (section_name, mod) in enumerate(mods, 1):
        url_display = mod.url if mod.url else "(no url)"
        notes_display = mod.notes if mod.notes else "(no notes)"
        print(f"{idx}. [{section_name}] {mod.name}\n     URL: {url_display}\n     Notes: {notes_display}")

def edit_mod(mod):
    clear_screen()
    open_mod_page(mod.name)
    print(f"\nEditing '{mod.name}'")
    print(mod)

    url = input(f"  Current URL: {mod.url or '(none)'}\n  New URL (or Enter to skip): ").strip()
    notes = input(f"  Current Notes: {mod.notes or '(none)'}\n  New Notes (or Enter to skip): ").strip()

    if url:
        mod.url = format_nexusmods_link(url)
    if notes:
        mod.notes = notes

    print("  ✅ Mod updated.\n")

def flatten_mods(mod_dict):
    """Return a list of (section_name, mod) tuples."""
    all_mods = []
    for section_name, section in mod_dict.sections.items():
        for mod in section.mods:
            all_mods.append((section_name, mod))
    return all_mods

def format_nexusmods_link(url: str) -> str:
    if "nexusmods.com/morrowind/mods/" in url:
        # Extract the mod ID from the URL
        mod_id = url.rstrip("/").split("/")[-1]
        return f"[{mod_id}]({url})"
    return url  # Return the original if it's not a Nexus Mods URL

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

# def open_mod_page(name):
#     # Format the name for the URL (replace spaces with + and make it lowercase)
#     formatted_name = name.replace(' ', '+').lower()
#     url = f'https://www.nexusmods.com/games/morrowind/search?keyword={formatted_name}'
    
#     # Open the URL in the default web browser
#     webbrowser.open(url)

def open_mod_page(name):
    query = f"morrowind {name}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    print(f"Searching: {encoded_query}")
    print(url)

    # Fetch the search results page
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')

    # Parse HTML to find the first result link
    parser = DuckDuckGoParser()
    parser.feed(html)

    # Get the prioritized link
    first_link = parser.get_priority_link()

    if first_link:
        webbrowser.open(first_link)
    else:
        print("No result found.")

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

    for section_name, section in mod_dict.sections.items():
        print(section)

    if args.walk:
        walk_missing_urls(mod_dict)
    else:
        interactive_selection(mod_dict)

if __name__ == "__main__":
    main()
