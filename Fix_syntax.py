import re

def fix_syntax_errors(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    stack = []  # Stack for tracking open brackets
    opening = {"(": ")", "[": "]", "{": "}"}
    closing = {")": "(", "]": "[", "}": "{"}

    fixed_lines = []
    open_strings = None  # To track unclosed string literals

    for line in lines:
        original_line = line.rstrip("\n")
        
        # Fix missing colons in function definitions, loops, and if statements
        if re.match(r"^\s*(if|elif|else|for|while|def|class) .*[^:]\s*$", original_line):
            original_line += ":"

        # Fix indentation (ensure it's a multiple of 4 spaces)
        stripped = original_line.lstrip()
        spaces = len(original_line) - len(stripped)
        if spaces % 4 != 0:
            spaces = (spaces // 4) * 4
        corrected_line = " " * spaces + stripped
        
        # Detect open brackets and strings
        for char in corrected_line:
            if char in opening:
                stack.append(char)
            elif char in closing:
                if stack and stack[-1] == closing[char]:
                    stack.pop()
            elif char in ('"', "'"):
                if open_strings is None:
                    open_strings = char  # Opening a string
                elif open_strings == char:
                    open_strings = None  # Closing a string

        fixed_lines.append(corrected_line)

    # Fix any unclosed brackets
    missing_closures = "".join(opening[char] for char in reversed(stack))
    if missing_closures:
        fixed_lines.append(missing_closures)

    # Fix unclosed string literals by adding closing quote
    if open_strings:
        fixed_lines[-1] += open_strings

    # Overwrite the original file
    with open(file_path, "w") as f:
        f.writelines(line + "\n" for line in fixed_lines)

    print(f"Syntax errors fixed in: {file_path}")

# Example usage
if __name__ == "__main__":
    file_path = "script.py"  # Replace with your Python file path
    fix_syntax_errors(file_path)
