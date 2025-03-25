import os
import re

def fix_syntax_errors(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    stack = []  # Track open parentheses
    fixed_lines = []
    inside_multiline_string = False  # Track if inside a multi-line string
    multiline_string_delimiter = None  # Store the delimiter type (''' or """)
    previous_line_continued = False  # Track if the previous line ended with '\'

    for line in lines:
        original_line = line.rstrip("\n")
        corrected_line = original_line

        # Fix missing colons in control structures
        if re.match(r"^\s*(if|elif|else|for|while|def|class) .*[^:]\s*$", corrected_line):
            corrected_line += ":"

        # Detect triple-quoted strings (""" or ''')
        triple_quote_match = re.findall(r'("""|\'\'\')', corrected_line)
        if triple_quote_match:
            delimiter = triple_quote_match[0]
            if inside_multiline_string and delimiter == multiline_string_delimiter:
                inside_multiline_string = False  # Closing a multi-line string
                multiline_string_delimiter = None
            else:
                inside_multiline_string = True  # Opening a multi-line string
                multiline_string_delimiter = delimiter

        # Handle multi-line strings or continued lines
        if corrected_line.endswith("\\"):
            previous_line_continued = True
            fixed_lines.append(corrected_line)
            continue  # Skip bracket checking for this line

        if inside_multiline_string or previous_line_continued:
            fixed_lines.append(corrected_line)
            previous_line_continued = False
            continue  # Skip bracket checking for this line

        # Detect function calls before `.cache()` and fix parentheses
        match = re.search(r"(\w+\s*=\s*[\w_]+\s*\([^\)]*)\.cache\(\)", corrected_line)
        if match:
            # Count open and close parentheses
            open_count = corrected_line.count("(")
            close_count = corrected_line.count(")")
            missing_closures = open_count - close_count

            if missing_closures > 0:
                corrected_line = corrected_line.replace(".cache()", ")" * missing_closures + ".cache()")

        fixed_lines.append(corrected_line)

    # Overwrite the original file
    with open(file_path, "w") as f:
        f.writelines(line + "\n" for line in fixed_lines)

    print(f"Fixed: {file_path}")

def fix_syntax_in_folder(folder_path):
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        return

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):  # Process only Python files
                file_path = os.path.join(root, file)
                fix_syntax_errors(file_path)

# Example usage
if __name__ == "__main__":
    folder_path = "path/to/your/folder"  # Change this to your folder path
    fix_syntax_in_folder(folder_path)
                     
