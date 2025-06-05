def move_types_to_column_45(input_path, output_path):
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            parts = line.strip().split()

            new_line = []
            for word in parts:
                if word in ('int', 'float'):
                    # Pad until column 45
                    space_needed = max(0, 44 - len(' '.join(new_line)))
                    new_line.append(' ' * space_needed + word)
                else:
                    new_line.append(word)

            outfile.write(' '.join(new_line) + '\n')


# Example usage
input_file = 'input.txt'
output_file = 'output.txt'
move_types_to_column_45(input_file, output_file)
