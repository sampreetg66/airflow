import ast

# Set of BigQuery-compatible data types
bq_types = {'float64', 'int', 'string', 'timestamp', 'bool'}

def cast_values(data):
    type_mapping = {}
    should_cast = False

    # Step 1: Extract type mappings and check for BQ types
    for key, value in data.items():
        if isinstance(value, str) and ':' in value:
            field, dtype = value.split(':', 1)
            if dtype in bq_types:
                type_mapping[key] = dtype
                should_cast = True

    # If no casting needed, return original
    if not should_cast:
        return data, False

    # Step 2: Apply CAST to matching fields
    for key, value in data.items():
        if isinstance(value, str) and ':' in value:
            field, val = value.split(':', 1)
            if key in type_mapping:
                cast_type = type_mapping[key]
                data[key] = f"CAST({val} AS {cast_type})"
    return data, True

input_file = 'input.txt'
output_file = 'output.txt'

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        if line.strip():  # skip empty lines
            try:
                row_dict = ast.literal_eval(line.strip())
                transformed_row, changed = cast_values(row_dict)
                outfile.write(str(transformed_row) + '\n')
            except Exception as e:
                # Write line unchanged if it cannot be parsed
                outfile.write(line)
                
