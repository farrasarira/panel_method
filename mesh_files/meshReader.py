import re

def parse_bem_file(file_path):
    bem_data = {}
    sections_data = {}
    
    with open(file_path, 'r') as file:
        lines = file.readlines()

    bem_data['file_path'] = file_path
    
    # Parse the header information
    header_pattern = re.compile(r'(\w[\w\s\/]*): ([\d\.\-\s,]+)')
    for i, line in enumerate(lines):
        match = header_pattern.match(line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            if ',' in value:
                value = [float(v) for v in value.split(',')]
            elif '.' in value:
                value = float(value)
            else:
                value = int(value)
            bem_data[key] = value
        if line.startswith("Radius/R"):
            break
    
    # Parse the main data table
    main_data_headers = lines[i].strip().split(', ')
    main_data = []
    i += 1
    while i < len(lines) and lines[i].strip():
        main_data.append([float(v) for v in lines[i].strip().split(', ')])
        i += 1
    
    bem_data['main_data'] = main_data
    bem_data['main_data_headers'] = main_data_headers
    
    # Parse the section data
    section_pattern = re.compile(r'Section (\d+) X, Y')
    while i < len(lines):
        match = section_pattern.match(lines[i])
        if match:
            section_number = int(match.group(1))
            section_coords = []
            i += 1
            while i < len(lines) and lines[i].strip():
                section_coords.append([float(v) for v in lines[i].strip().split(', ')])
                i += 1
            sections_data[section_number] = section_coords
        i += 1
    
    bem_data['sections'] = sections_data
    
    return bem_data


def print_bem_data(bem_data):

    # create file
    file_path = bem_data['file_path'].replace(".bem",".x")
    f = open(file_path, "w")

    num_blocks = 1
    num_nodes_dirx = len(bem_data['sections'][0])
    num_nodes_diry = len(bem_data['sections'])

    radius = bem_data['Diameter'] / 2.0
    
    f.write(f"{num_blocks}\n")
    f.write(f"{num_nodes_dirx}\t{num_nodes_diry}\t{1}\n")

    for i in range(num_nodes_diry):
        for j in range(num_nodes_dirx):
            chord_len = bem_data['main_data'][i][1]*radius
            f.write(f"{bem_data['sections'][i][j][0]*chord_len}\n")

    for i in range(num_nodes_diry):
        for j in range(num_nodes_dirx):
            chord_len = bem_data['main_data'][i][1]*radius
            f.write(f"{bem_data['sections'][i][j][1]*chord_len}\n")
    
    for i in range(num_nodes_diry):
        for j in range(num_nodes_dirx):
            f.write(f"{bem_data['main_data'][i][0]*radius}\n")
    
    f.close()

import sys

file_path = sys.argv[1] 
bem_data = parse_bem_file(file_path)
print_bem_data(bem_data)
