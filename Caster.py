import re

# List of valid BigQuery types
bq_types = {'float64', 'int', 'string', 'timestamp', 'bool'}

# Regex to match key-value pairs like 'key': 'value'
pair_pattern = re.compile(r"'(\w+)'\s*:\s*'([^']*)'")

input_file = 'input.txt'
output_file = 'output.txt'

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        original_line = line.strip()
        if not original_line:
            continue

        try:
            # Parse all key-value pairs into a dict
            kv_pairs = dict(pair_pattern.findall(original_line))

            # Look for the data type definition (e.g., from key 'd')
            dtype = None
            for k, v in kv_pairs.items():
                if v in bq_types:
                    dtype = v
                    break

            # If no type found, or no 'i3' key, just write the line as-is
            if not dtype or 'i3' not in kv_pairs:
                outfile.write(original_line + '\n')
                continue

            # Update 'i3' value with CAST(...)
            val = kv_pairs['i3']
            kv_pairs['i3'] = f"CAST({val} AS {dtype})"

            # Reconstruct the line
            updated_line = '{' + ', '.join(f"'{k}': '{v}'" for k, v in kv_pairs.items()) + '}'
            outfile.write(updated_line + '\n')

        except Exception:
            # If anything goes wrong, write the original line
            outfile.write(original_line + '\n')
            
