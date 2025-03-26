import os
import re

def fix_syntax_errors(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    fixed_lines = []  # Store corrected lines
    open_parens_stack = []  # Stack to track open '(' positions
    inside_multiline_string = False
    multiline_string_delimiter = None
    modified_lines = []  # Track modified line numbers

    i = 0
    while i < len(lines):
        corrected_line = lines[i].rstrip("\n")  # Strip newline to avoid extra blank lines

        # Detect multi-line strings (both triple and single/double quotes)
        triple_quote_match = re.findall(r'("""|\'\'\'|["\'])', corrected_line)
        if triple_quote_match:
            delimiter = triple_quote_match[0]
            if inside_multiline_string and delimiter == multiline_string_delimiter:
                inside_multiline_string = False
                multiline_string_delimiter = None
            else:
                inside_multiline_string = True
                multiline_string_delimiter = delimiter

        # If inside a multi-line string, skip syntax fixes
        if inside_multiline_string:
            fixed_lines.append(corrected_line)
            i += 1
            continue

        # Track open/close parenthesis count across lines
        open_count = corrected_line.count("(")
        close_count = corrected_line.count(")")
        open_parens_stack.append(open_count - close_count)

        # Fix missing closing parentheses before `.cache()`
        match = re.search(r"(\w+\s*=\s*[\w_]+\s*\([^\)]*)\.cache\(\)", corrected_line)
        if match:
            missing_closures = sum(open_parens_stack)  # Count missing `)` to close
            if missing_closures > 0:
                corrected_line = re.sub(r"(\.cache\(\))", ")" * missing_closures + r"\1", corrected_line)
                open_parens_stack.clear()  # Reset stack after fixing
                modified_lines.append(i + 1)

        # Fix issue where `.cache()` follows a line continued with `\`
        if ")." in corrected_line:  
            # Go back until we find the first non-`\` line
            backtrack_index = i - 1
            while backtrack_index >= 0 and lines[backtrack_index].rstrip().endswith("\\"):
                backtrack_index -= 1

            # The line to check is the one *after* the first non-`\` line
            check_line_index = backtrack_index + 1

            if 0 <= check_line_index < len(lines) and "run_bq_query(bq_query_formating(" in lines[check_line_index]:
                # Count open `(` and closed `)` to see if an extra `)` is needed
                open_parens = sum(l.count("(") for l in lines[check_line_index:i+1])
                close_parens = sum(l.count(")") for l in lines[check_line_index:i+1])

                if open_parens > close_parens:  # Only fix if extra `)` is needed
                    corrected_line = corrected_line.replace(").", ")).")
                    modified_lines.append(i + 1)

        fixed_lines.append(corrected_line)
        i += 1

    # Save fixed content
    with open(file_path, "w") as f:
        f.writelines(line + "\n" for line in fixed_lines)

    # Log changes
    if modified_lines:
        log_file = r"<log_file_path>"  # Set the correct log path
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)  # Ensure directory exists
            with open(log_file, "a") as log:
                log.write(f"Fixed: {file_path}\n")
                log.write(f"Modified lines: {modified_lines}\n\n")
            print(f"Fixed: {file_path} (Lines {modified_lines})")
        except Exception as e:
            print(f"Error writing to log file: {e}")

# Example usage
if __name__ == "__main__":
    file_path = r"..\test.py"  # Change this
    fix_syntax_errors(file_path)
