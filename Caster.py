import re

# Set of allowed BigQuery types
bq_types = {'float64', 'int', 'string', 'timestamp', 'bool'}

# Regex pattern to match key-value pairs like 'key': 'value:type'
pattern = re.compile(r"'(\w+)'\s*:\s*'([^']+):([^']+)'")

input_file = 'input.txt'
output_file = 'output.txt'

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        # Function to handle replacement
        def replace_cast(match):
            key = match.group(1)
            value = match.group(2)
            dtype = match.group(3)
            if dtype in bq_types:
                return f"'{key}': 'CAST({value} AS {dtype})'"
            else:
                return match.group(0)  # return original match

        # Substitute with regex
        modified_line = pattern.sub(replace_cast, line)

        outfile.write(modified_line)
        
