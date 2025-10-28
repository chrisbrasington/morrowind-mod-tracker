import sys
import os
import re

def simplify_markdown_to_table(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    output_lines = []
    current_type = ""
    in_table = False

    url_regex = re.compile(r'\[(\d+)\]\((https?://[^\)]+)\)')

    # Write table header
    output_lines.append("| Type | Name | Description |")
    output_lines.append("|------|------|-------------|")

    for line in lines:
        stripped = line.strip()

        # Capture section as Type (## ...)
        if stripped.startswith("## "):
            current_type = stripped[3:]  # drop "## "
            in_table = False
            continue

        # Recognize table start
        if stripped.startswith("| Name"):
            in_table = True
            continue

        if in_table:
            # End of table section
            if not stripped.startswith("|"):
                in_table = False
                continue

            cells = [c.strip() for c in stripped.split("|")]
            if len(cells) < 4 or cells[1] == "Name":
                continue

            name = cells[1]
            notes = cells[2]
            url_field = cells[3]

            match = url_regex.search(url_field)
            if not match:
                continue

            url = match.group(2)
            name_link = f"[{name}]({url})"

            output_lines.append(f"| {current_type} | {name_link} | {notes} |")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"✅ Simplified table written to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python simplify_table.py <input.md> [output.md]")
        sys.exit(1)

    input_file = sys.argv[1]

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_table{ext}"

    simplify_markdown_to_table(input_file, output_file)
