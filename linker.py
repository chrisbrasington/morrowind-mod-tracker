import argparse
import os, platform, sys, webbrowser
from classes import ModDictionary
#from duckduckgo_search import DDGS
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urlparse, parse_qs

MARKDOWN_PATH = "README.md"
last_url = None
last_notes = None
last_search_query = None

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

                cleaned_url = cleaned_url.split('?')[0]

                if 'nexusmods.com' in cleaned_url:
                    nexusmods_urls.append(cleaned_url)
                elif 'modding-openmw.com' in cleaned_url:
                    modding_openmw_urls.append(cleaned_url)
                else:
                    other_urls.append(cleaned_url)

        # Concatenate the lists with priority (nexusmods.com > modding-openmw.com > others)
        sorted_urls = nexusmods_urls + modding_openmw_urls + other_urls

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
    global last_url, last_notes
    clear_screen()

    print(f"\nEditing '{mod.name}'")
    print(mod)

    search_result = open_mod_page(mod.name)
    if search_result == "reuse":
        if last_url:
            mod.url = last_url
        if last_notes:
            mod.notes = last_notes
        print("  ✅ Mod auto-updated.\n")
        return
    elif isinstance(search_result, str):
        # A new URL was opened and set
        last_url = search_result

    print()
    print(f'Last url: {last_url}')
    print(f'Last notes: {last_notes}')
    print()

    # Prompt user for URL
    url_prompt = f"  Current URL: {mod.url or '(none)'}\n"
    if last_url:
        url_prompt += "  New URL (Enter to skip, 'ditto' or 'd' to reuse last): "
    else:
        url_prompt += "  New URL (Enter to skip): "
    url_input = input(url_prompt).strip()

    # Prompt user for Notes
    notes_prompt = f"  Current Notes: {mod.notes or '(none)'}\n"
    if last_notes:
        notes_prompt += "  New Notes (Enter to skip, 'ditto' or 'd' to reuse last): "
    else:
        notes_prompt += "  New Notes (Enter to skip): "
    notes_input = input(notes_prompt).strip()

    # Handle URL input
    if last_url and url_input.lower() in ("ditto", "d"):
        url = last_url
    elif url_input:
        url = format_hyperlink(url_input)
        last_url = url
    else:
        url = None

    # Handle Notes input
    if last_notes and notes_input.lower() in ("ditto", "d"):
        notes = last_notes
    elif notes_input:
        notes = notes_input
        last_notes = notes
    else:
        notes = None

    if url:
        mod.url = url
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

def format_hyperlink(url: str) -> str:
    if "nexusmods.com/morrowind/mods/" in url:
        # Extract the mod ID from the URL
        mod_id = url.rstrip("/").split("/")[-1]
        return f"[{mod_id}]({url})"
    elif 'modding-openmw.com/mods/' in url:
        mod_id = url.split('mods/')[-1].rstrip('/')
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

def open_mod_page(mod_name):
    global last_url
    query = f"morrowind {mod_name}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

    print(f"\n🔍 Searching: {url}")

    # Fetch the search results page
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')

    parser = DuckDuckGoParser()
    parser.feed(html)
    first_link = parser.get_priority_link()

    if first_link:
        # If it's the same as the last opened, prompt to reuse
        if first_link == last_url:
            print(f"🔁 Same URL as last opened:\n   ➤ URL: {last_url or '(none)'}\n   ➤ Notes: {last_notes or '(none)'}")
            confirm = input("   Use same URL and Notes? [Y/n] (enter for Y): ").strip().lower()
            if confirm in ("", "y"):
                return "reuse"
        else:
            webbrowser.open(first_link)
            last_url = first_link
            return first_link
    else:
        print("❌ No result found.")
        return None


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

    print('\nDONE')

if __name__ == "__main__":
    main()
