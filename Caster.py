import ast

def cast_values(data):
    type_mapping = {}
    # First, collect type mapping from the row
    for key, value in data.items():
        if isinstance(value, str) and ':' in value:
            field, dtype = value.split(':', 1)
            if dtype in ['float64', 'int', 'tt', 'ad', 'a_ad']:
                type_mapping[key] = dtype

    # Now, apply the cast
    for key, value in data.items():
        if isinstance(value, str) and ':' in value:
            field, val = value.split(':', 1)
            if key in type_mapping:
                cast_type = type_mapping[key]
                data[key] = f"CAST({val} AS {cast_type})"
    return data

input_file = 'input.txt'
output_file = 'output.txt'

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        if line.strip():  # skip empty lines
            row_dict = ast.literal_eval(line.strip())
            transformed = cast_values(row_dict)
            outfile.write(str(transformed) + '\n')
