import argparse
import os
import re

# Configuration
DOCS_ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE_ROOT = os.path.join(DOCS_ROOT, "source")


def unescape_po_string(text):
    """
    Unescapes PO string content.
    Handles \\, \", \n, \t correctly using regex to avoid double-unescaping issues.
    This replaces sequences like \\" with " and \\\\ with \\.
    """

    def callback(match):
        c = match.group(1)
        if c == "\\":
            return "\\"
        if c == '"':
            return '"'
        if c == "n":
            return "\n"
        if c == "t":
            return "\t"
        return match.group(0)  # Keep as is for others

    return re.sub(r"\\(.)", callback, text)


def parse_po(po_path):
    """
    Parses a .po file and returns a list of entries.
    Each entry is a dict with 'msgid' and 'msgstr'.
    Handles multi-line strings and unescaping.
    """
    entries = []
    current_entry = {}
    state = None

    if not os.path.exists(po_path):
        return []

    with open(po_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue

        if line.startswith("msgid "):
            if "msgid" in current_entry:
                entries.append(current_entry)
                current_entry = {}
            state = "msgid"
            content = line[6:].strip()
            # Handle quoted string on the same line
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
                content = unescape_po_string(content)
            else:
                # msgid "" case, usually followed by lines
                if content == '""':
                    content = ""

            current_entry["msgid"] = content

        elif line.startswith("msgstr "):
            state = "msgstr"
            content = line[7:].strip()
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
                content = unescape_po_string(content)
            else:
                if content == '""':
                    content = ""

            # The strip() is crucial here to remove leading/trailing whitespace
            # from the translation string, if any was left by parser or exists in PO
            current_entry["msgstr"] = content

        elif line.startswith('"') and line.endswith('"'):
            # Continuation line
            content = line[1:-1]
            # Unescape basic characters using the robust function
            content = unescape_po_string(content)

            if state == "msgid":
                current_entry["msgid"] += content
            elif state == "msgstr":
                current_entry["msgstr"] += content

    if "msgid" in current_entry:
        entries.append(current_entry)

    # Strip whitespace from all msgids and msgstrs after full assembly
    for entry in entries:
        if "msgid" in entry:
            entry["msgid"] = entry["msgid"].strip()
        if "msgstr" in entry:
            entry["msgstr"] = entry["msgstr"].strip()

    return entries


def load_global_translations(locale_root):
    """
    Loads all translations from all PO files in the locale directory into a single dictionary.
    Used for fallback when a specific PO file has missing translations (e.g. included files).
    """
    tm = {}
    print(f"Loading global translation memory from {locale_root}...")
    for root, dirs, files in os.walk(locale_root):
        for file in files:
            if file.endswith(".po"):
                po_path = os.path.join(root, file)
                entries = parse_po(po_path)
                for entry in entries:
                    msgid = entry.get("msgid")
                    msgstr = entry.get("msgstr")
                    if msgid and msgstr:
                        # We just overwrite if duplicates exist.
                        # This assumes consistent translations across the project.
                        tm[msgid] = msgstr
    print(f"Loaded {len(tm)} global translations.")
    return tm


def reformat_grid_table(table_lines):
    """
    Parses and reformats a Grid Table to fit its content.
    Adjusts column widths based on the max length of cell contents.
    """
    if not table_lines:
        return []

    # 1. Parse Structure
    # We rely on separators to define row boundaries, but we need to know column count.
    # We assume the first separator defines the column structure (unless spans are involved).
    # Simple grid tables only.

    # Analyze the first separator to count columns
    # +-------+-------+ -> parts: '', '-------', '-------', '' -> 2 columns

    first_sep = table_lines[0].strip()
    col_count = first_sep.count("+") - 1
    if col_count < 1:
        return table_lines  # Not a valid grid table

    # We iterate through lines to parse
    # Structure:
    # Sep
    # Row Content (can be multiline)
    # Sep
    # ...

    table_structure = []  # List of ('sep', char) or ('row', cells_list)

    idx = 0
    while idx < len(table_lines):
        line = table_lines[idx].strip()

        if line.startswith("+"):
            # It's a separator
            # Determine type (- or =)
            sep_char = "-"
            if "=" in line:
                sep_char = "="
            table_structure.append(("sep", sep_char))
            idx += 1
        elif line.startswith("|"):
            # It's a content row (potentially multiline)
            # Gather all content lines until next separator
            row_lines = []
            while idx < len(table_lines) and table_lines[idx].strip().startswith("|"):
                row_lines.append(table_lines[idx].strip())
                idx += 1

            # Parse these lines into cells
            # Each line looks like "| cell 1 | cell 2 |"
            cells = [[] for _ in range(col_count)]
            for r_line in row_lines:
                # remove leading and trailing |
                if r_line.startswith("|"):
                    r_line = r_line[1:]
                if r_line.endswith("|"):
                    r_line = r_line[:-1]

                parts = r_line.split("|")
                # We expect len(parts) == col_count

                for c_i, part in enumerate(parts):
                    if c_i < col_count:
                        cells[c_i].append(part.strip())

            table_structure.append(("row", cells))
        else:
            # Unknown line type?
            idx += 1

    # 2. Calculate widths
    col_widths = [0] * col_count

    for item_type, item_data in table_structure:
        if item_type == "row":
            cells = item_data
            for i, cell_lines in enumerate(cells):
                # Max width of any line in this cell
                w = 0
                for line in cell_lines:
                    # We want visual width (len).
                    w = max(w, len(line))
                col_widths[i] = max(col_widths[i], w)

    # Add padding (+2 for " text " spaces)
    col_widths = [w + 2 for w in col_widths]

    # 3. Render
    output = []

    for item_type, item_data in table_structure:
        if item_type == "sep":
            sep_char = item_data
            # Build separator line: +-------+-------+
            line_parts = []
            for w in col_widths:
                line_parts.append(sep_char * w)
            line = "+" + "+".join(line_parts) + "+"
            output.append(line)

        elif item_type == "row":
            cells = item_data
            # We need to determine how many physical lines this row occupies
            height = max(len(c) for c in cells) if cells else 0

            for h in range(height):
                line_parts = []
                for i in range(col_count):
                    # Get content for this line, or empty string
                    cell_lines = cells[i]
                    text = cell_lines[h] if h < len(cell_lines) else ""
                    width = col_widths[i]
                    # Format: " text " padded to width
                    # We added 2 to width for padding.
                    # So we pad text with 1 space left, and rest right.
                    content = " " + text
                    line_parts.append(content.ljust(width))

                line = "|" + "|".join(line_parts) + "|"
                output.append(line)

    return output


def fix_rst_tables(content):
    """
    Scans content for Grid Tables and reformats them.
    Identifies table blocks (starting with +---) and calls reformat_grid_table.
    """
    lines = content.split("\n")
    new_lines = []
    i = 0

    # Regex for grid table separator: +---+ or +===+
    # It must start with + and end with +
    sep_pattern = re.compile(r"^\s*\+[-=+]+\+\s*$")
    # Regex for grid table row: | text | text |
    row_pattern = re.compile(r"^\s*\|.*\|\s*$")

    while i < len(lines):
        line = lines[i]

        # Check start of table (must be a separator)
        if sep_pattern.match(line):
            table_lines = [line]
            i += 1

            # Consume table block
            while i < len(lines):
                next_line = lines[i]
                if sep_pattern.match(next_line) or row_pattern.match(next_line):
                    table_lines.append(next_line)
                    i += 1
                else:
                    break

            # Process table
            try:
                fixed_table = reformat_grid_table(table_lines)
                if fixed_table:
                    new_lines.extend(fixed_table)
                else:
                    new_lines.extend(table_lines)
            except Exception as e:
                print(f"Warning: Failed to fix table: {e}")
                new_lines.extend(table_lines)
        else:
            new_lines.append(line)
            i += 1

    return "\n".join(new_lines)


def swap_rst_content(rst_content, entries):
    """
    Replaces msgid text with msgstr text in the RST content.
    Adjusts RST underlines (e.g., ====, ----) to match new text length.
    Uses a placeholder strategy to prevent double-replacement of substrings.
    """
    # Protect graphviz blocks from translation
    graphviz_placeholders = {}
    graphviz_counter = 0

    # Pattern to match .. graphviz:: directive and its content
    # Matches: .. graphviz:: followed by optional blank line and indented content
    # Content continues until we hit a non-indented line (or end of file)
    graphviz_pattern = re.compile(r"^(\.\.\s+graphviz::\s*$\n(?:\s*$\n)?)((?:^[ \t]+.*$\n?)+)", re.MULTILINE)

    def replace_graphviz(match):
        nonlocal graphviz_counter
        placeholder = f"__GRAPHVIZ_PH_{graphviz_counter}__"
        graphviz_placeholders[placeholder] = match.group(0)
        graphviz_counter += 1
        return placeholder

    new_content = graphviz_pattern.sub(replace_graphviz, rst_content)
    # Sort by length to match longest strings first to avoid partial replacements
    entries = [e for e in entries if e.get("msgid")]
    # CRITICAL: Sort by length descending so longer strings match first
    entries.sort(key=lambda x: len(x["msgid"]), reverse=True)

    placeholders = {}
    placeholder_counter = 0
    # Track which msgids have been successfully matched to prevent shorter substrings from matching
    matched_msgids = set()

    # Note: We rely on length sorting (longer strings processed first) and the placeholder
    # strategy to prevent shorter substrings from matching parts of longer strings.
    # If a longer string matches, it creates a placeholder, and the shorter string won't
    # match that placeholder. If the longer string doesn't match, the shorter string can
    # still match its independent instances.

    for entry in entries:
        msgid = entry["msgid"]
        msgstr = entry["msgstr"]

        # Normalize msgid for comparison (should already be stripped by parse_po, but be safe)
        msgid_normalized = msgid.strip() if msgid else ""

        if not msgstr:
            # Keep original text if no translation available, but allow header fixing
            # by treating msgid as the target text.
            msgstr = msgid

        # Clean msgid for regex construction
        # Since msgid is already unescaped by parse_po, just strip whitespace
        clean_msgid = msgid_normalized
        words = clean_msgid.split()
        if not words:
            continue

        # Escape for regex with optional whitespace handling around punctuation
        escaped_words = []
        for w in words:
            # Check for trailing punctuation (e.g. "string," or "word.")
            m = re.match(r"^(.*?)([.,;:!?]+)$", w)
            if m:
                # word + punctuation -> allow whitespace between them
                base = re.escape(m.group(1))
                punct = re.escape(m.group(2))
                escaped_words.append(f"{base}\\s*{punct}")
            else:
                escaped_words.append(re.escape(w))

        # Generate a unique placeholder
        placeholder = f"__SWAP_PH_{placeholder_counter}__"
        placeholders[placeholder] = msgstr
        placeholder_counter += 1

        # Pattern to match the text followed strictly by a newline and an underline
        # The underline chars are usually = - ~ ` ^ " * + # '
        underline_chars = r'= \- ~ ` \^ " \* \+ # \''

        # Regex explanation:
        # 1. Match start of line and indentation (^\s*) -> Group 1
        # 2. Match the phrase allowing whitespace between words -> Group 2
        # 3. Followed by EXACTLY ONE newline (\n) -> Group 3
        # 4. Followed by a line of underline characters -> Group 4
        # Note: We anchor to start of line (^) to prevent partial matches (e.g. "Item" matching inside "BidItem")

        pattern_str = r"(^\s*)(" + r"\s+".join(escaped_words) + r")(\n)([" + underline_chars + r"]{3,})[ \t]*$"

        # We need multiline to match end of line $ properly for underline, and ^ for start of line
        pattern = re.compile(pattern_str, re.MULTILINE)

        # Function to replace text AND resize underline
        def replacement_func(match):
            indentation = match.group(1)
            original_text_block = match.group(2)  # noqa: F841
            spacing = match.group(3)
            underline = match.group(4)

            # The new text is msgstr (already unescaped by parse_po)
            # We use the final msgstr here to calculate length, but replace text with placeholder
            final_text = msgstr

            # Determine new underline length based on the last line of the new text
            last_line_len = len(final_text.split("\n")[-1])

            # Resize underline
            # Fix: Use new_text length if it's larger, or stick to convention.
            # RST requires underline to be >= title length.
            # We strictly use the title length.
            new_underline = underline[0] * last_line_len

            # Return PLACEHOLDER instead of text, but keep the resized underline
            return indentation + placeholder + spacing + new_underline

        # First pass: try to replace Headers (text + underline)
        # This replaces instances where the text is followed by an underline
        new_content_with_headers = pattern.sub(replacement_func, new_content)

        if new_content_with_headers != new_content:
            new_content = new_content_with_headers
            matched_msgids.add(msgid_normalized)  # Track successful match

        # Second pass: Always try simple pattern to catch instances without underlines
        # (even if header pattern matched some instances, there may be more without underlines)
        # Add word boundaries to avoid partial matches (e.g. "plain" inside "complaints")
        pattern_parts = []

        # Check start boundary
        if re.match(r"^\w", words[0]):
            pattern_parts.append(r"\b")

        pattern_parts.append(r"\s+".join(escaped_words))

        # Check end boundary
        # re.match() checks from start, so we use re.search() to check if string ends with word char
        if words[-1] and re.search(r"\w$", words[-1]):
            pattern_parts.append(r"\b")

        simple_pattern_str = "".join(pattern_parts)

        try:
            simple_pattern = re.compile(simple_pattern_str)
            # Replace with PLACEHOLDER
            # Check if replacement actually happened
            old_content = new_content
            new_content = simple_pattern.sub(lambda m: placeholder, new_content)
            if new_content != old_content:
                matched_msgids.add(msgid_normalized)  # Track successful match
        except re.error:
            continue

    # Final pass: Replace all placeholders with actual msgstr
    # Sort by placeholder number to ensure consistent order
    def get_ph_num(ph):
        try:
            return int(ph.split("_")[-1].rstrip("_"))
        except (ValueError, IndexError):
            return 0

    for ph, text in sorted(placeholders.items(), key=lambda x: get_ph_num(x[0])):
        new_content = new_content.replace(ph, text)

    # Fix tables after all replacements
    new_content = fix_rst_tables(new_content)

    # Restore graphviz blocks
    for placeholder, graphviz_block in graphviz_placeholders.items():
        new_content = new_content.replace(placeholder, graphviz_block)

    return new_content


def generate_reverse_po(entries, output_path, src_lang, dest_lang):
    """
    Generates a new PO file where msgid is the msgstr text and msgstr is the msgid text.
    Preserves header metadata but updates Language from src_lang to dest_lang.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    header_entry = next((e for e in entries if e["msgid"] == ""), None)

    with open(output_path, "w", encoding="utf-8") as f:
        # Write header
        f.write('msgid ""\n')
        f.write('msgstr ""\n')

        if header_entry and header_entry.get("msgstr"):
            metadata = header_entry["msgstr"]
            # Update Language fields
            metadata = metadata.replace(f"Language: {src_lang}", f"Language: {dest_lang}")
            metadata = metadata.replace(f"Language-Team: {src_lang}", f"Language-Team: {dest_lang}")

            # Split by newline to write as PO strings
            # Note: parse_po converts \\n to \n, so we split by \n
            lines = metadata.split("\n")
            for line in lines:
                if not line:
                    continue
                # Escape for PO
                line_esc = line.replace("\\", "\\\\").replace('"', '\\"')
                f.write(f'"{line_esc}\\n"\n')
        else:
            # Fallback default header
            f.write('"Content-Type: text/plain; charset=UTF-8\\n"\n')
            f.write(f'"Language: {dest_lang}\\n"\n')

        f.write("\n")

        for entry in entries:
            msgid = entry["msgid"]
            msgstr = entry["msgstr"]

            if not msgid:  # Skip header entry in main loop
                continue

            # Helper to escape for PO format
            def escape_po(text):
                # 1. Escape backslashes first (so \ -> \\)
                # 2. Escape quotes (" -> \")
                # 3. Escape newlines (\n -> \n"\n")
                return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", '\\n"\n"')

            if not msgstr:
                # Fallback: RST remains original, so we need original -> original mapping
                # But user requested "only msgid", which means msgstr should be empty ""
                # This makes it an "untranslated" entry in the new PO file
                new_msgid = escape_po(msgid)
                new_msgstr = ""
            else:
                # Swap: msgid becomes translation (from old msgstr), msgstr becomes original (from old msgid)
                new_msgid = escape_po(msgstr)
                new_msgstr = escape_po(msgid)

            f.write(f'msgid "{new_msgid}"\n')
            f.write(f'msgstr "{new_msgstr}"\n')
            f.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Swap languages in RST files and generate reverse PO files.")
    parser.add_argument(
        "src_lang", help="Source language code (e.g. uk) - the language to swap INTO the RST files (from existing POs)"
    )
    parser.add_argument(
        "dest_lang", help="Destination language code (e.g. en) - the language to generate reverse PO files for"
    )

    args = parser.parse_args()
    src_lang = args.src_lang
    dest_lang = args.dest_lang

    locale_src_root = os.path.join(DOCS_ROOT, "locale", src_lang, "LC_MESSAGES")
    locale_dest_root = os.path.join(DOCS_ROOT, "locale", dest_lang, "LC_MESSAGES")

    print(f"Starting language swap: {src_lang} -> RST -> {dest_lang} POs")
    print(f"Reading translations from: {locale_src_root}")
    print(f"Generating reverse POs in: {locale_dest_root}")

    # Load Global Translations (fallback memory)
    global_tm = load_global_translations(locale_src_root)

    # Walk through source directory
    for root, dirs, files in os.walk(SOURCE_ROOT):
        for file in files:
            if not file.endswith(".rst"):
                continue

            rst_path = os.path.join(root, file)
            rel_path = os.path.relpath(rst_path, SOURCE_ROOT)

            # Determine corresponding PO path in locale/src_lang
            po_rel_path = rel_path.replace(".rst", ".po")
            po_path = os.path.join(locale_src_root, po_rel_path)

            if os.path.exists(po_path):
                print(f"Processing {rel_path}...")
                entries = parse_po(po_path)

                # Fill missing translations from Global TM
                for entry in entries:
                    if not entry.get("msgstr") and entry.get("msgid"):
                        msgid = entry["msgid"]
                        # Heuristic: Only fill if msgid looks like a sentence or phrase (has space)
                        # to avoid injecting generic short terms that cause partial replacement issues.
                        if " " in msgid and msgid in global_tm:
                            entry["msgstr"] = global_tm[msgid]

                # Read RST
                with open(rst_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Swap content
                new_content = swap_rst_content(content, entries)

                # Write back to RST
                with open(rst_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                # Generate reverse PO in locale/dest_lang
                en_po_path = os.path.join(locale_dest_root, po_rel_path)
                generate_reverse_po(entries, en_po_path, src_lang, dest_lang)
            else:
                pass

    print("Completed language swap.")


if __name__ == "__main__":
    main()
