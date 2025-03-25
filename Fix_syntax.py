import os
import re

def fix_syntax_errors(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    stack = []  # Stack for tracking open brackets
    opening = {"(": ")", "[": "]", "{": "}"}
    closing = {")": "(", "]": "[", "}": "{"}

    fixed_lines = []
    open_string = None  # Track unclosed string literals
    inside_multiline_string = False  # Track if inside a multi-line string
    multiline_string_delimiter = None  # Store the delimiter type (''' or """)
    previous_line_continued = False  # Track if the previous line ended with '\'

    for i, line in enumerate(lines):
        original_line = line.rstrip("\n")

        # Fix missing colons in control structures
        if re.match(r"^\s*(if|elif|else|for|while|def|class) .*[^:]\s*$", original_line):
            original_line += ":"

        # Fix indentation (ensure it's a multiple of 4 spaces)
        stripped = original_line.lstrip()
        spaces = len(original_line) - len(stripped)
        if spaces % 4 != 0:
            spaces = (spaces // 4) * 4
        corrected_line = " " * spaces + stripped

        # Detect and close function calls before .cache()
        match = re.search(r"(\w+\s*=\s*[\w_]+\s*\([^\)]*)\.cache\(\)", corrected_line)
        if match:
            corrected_line = corrected_line.replace(".cache()", ") .cache()")

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

        # Handle single- or double-quoted multi-line strings (continued with \)
        if corrected_line.endswith("\\"):
            previous_line_continued = True
            fixed_lines.append(corrected_line)
            continue  # Skip bracket checking for this line

        # Handle multi-line strings (continued without \)
        if inside_multiline_string or previous_line_continued:
            fixed_lines.append(corrected_line)
            previous_line_continued = False
            continue  # Skip bracket checking for this line

        # Detect unclosed single- or double-quoted strings
        for char in corrected_line:
            if char in ('"', "'"):
                if open_string is None:
                    open_string = char  # Opening a string
                elif open_string == char:
                    open_string = None  # Closing a string
            elif char in opening:
                stack.append(char)
            elif char in closing:
                if stack and stack[-1] == closing[char]:
                    stack.pop()

        fixed_lines.append(corrected_line)

    # Fix any unclosed brackets
    missing_closures = "".join(opening[char] for char in reversed(stack))
    if missing_closures:
        fixed_lines.append(missing_closures)

    # Fix unclosed string literals by adding closing quote
    if open_string:
        fixed_lines[-1] += open_string

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
    
