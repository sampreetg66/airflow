import os
import re

def fix_syntax_errors(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    fixed_lines = []
    temp_lines = []  # Stores multi-line statement
    inside_multiline = False  # Tracks if inside a multi-line expression

    for line in lines:
        stripped_line = line.rstrip("\n")

        # Handle line continuation (backslash `\`)
        if stripped_line.endswith("\\"):
            temp_lines.append(stripped_line)  # Store multi-line parts
            inside_multiline = True
            continue  # Wait until the full expression is collected

        if inside_multiline:
            temp_lines.append(stripped_line)  # Append the last part
            full_line = "\n".join(temp_lines)  # Preserve multi-line formatting
            inside_multiline = False  # Reset flag
            temp_lines = []  # Reset storage
        else:
            full_line = stripped_line

        # Fix function calls before `.cache()`
        match = re.search(r"(\w+\s*=\s*[\w_]+\s*\([^\)]*)\.cache\(\)", full_line)
        if match:
            # Count open and close parentheses
            open_count = full_line.count("(")
            close_count = full_line.count(")")
            missing_closures = open_count - close_count

            if missing_closures > 0:
                full_line = re.sub(r"(\.cache\(\))", ")" * missing_closures + r"\1", full_line)

        fixed_lines.append(full_line)

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
if __name__ == "__
