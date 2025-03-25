import os
import re

def fix_syntax_errors(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    fixed_lines = []
    temp_line = ""  # Holds multi-line expressions
    inside_multiline = False  # Tracks if inside a multi-line expression

    for line in lines:
        original_line = line.rstrip("\n")

        # Handle line continuation (backslash `\`)
        if original_line.endswith("\\"):
            temp_line += original_line.rstrip("\\")  # Append without the backslash
            inside_multiline = True
            continue  # Skip adding to fixed_lines until we have a complete expression

        if inside_multiline:
            temp_line += original_line  # Append continued line
            inside_multiline = False  # End multi-line tracking
            corrected_line = temp_line
            temp_line = ""  # Reset temp storage
        else:
            corrected_line = original_line

        # Fix function calls before `.cache()`
        match = re.search(r"(\w+\s*=\s*[\w_]+\s*\([^\)]*)\.cache\(\)", corrected_line)
        if match:
            # Count open and close parentheses
            open_count = corrected_line.count("(")
            close_count = corrected_line.count(")")
            missing_closures = open_count - close_count

            if missing_closures > 0:
                corrected_line = re.sub(r"(\.cache\(\))", ")" * missing_closures + r"\1", corrected_line)

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
    
