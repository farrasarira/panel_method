import re
import math
import numpy as np

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
    chord_list = list(np.array([colomn[1] for colomn in bem_data['main_data']]) * radius)
    spanwise_list = list(np.array([colomn[0] for colomn in bem_data['main_data']]) * radius)
    twist_angle_rad_list = list( np.radians(np.array([colomn[2] for colomn in bem_data['main_data']])) )

    airfoil_coords_dim = []
    for iter_section in reversed(range(bem_data['Num_Sections'])):
        airfoil_coords_ndim = bem_data['sections'][iter_section]
        chord = chord_list[iter_section]
        leading_edge = [
            0.0 - 0.5*chord,
            -1*spanwise_list[iter_section],
            0.0
        ]
        twist_angle_rad = twist_angle_rad_list[iter_section]
        
        airfoil_coords_dim.append(dimensionalize_coordinates(airfoil_coords_ndim, leading_edge, chord, twist_angle_rad))
    
    f.write(f"{num_blocks}\n")
    f.write(f"{num_nodes_dirx}\t{num_nodes_diry}\t{1}\n")


    for i in range(num_nodes_diry):
        for j in range(num_nodes_dirx):
            f.write("%f\n" % airfoil_coords_dim[i][j][0])

    for i in range(num_nodes_diry):
        for j in range(num_nodes_dirx):
            f.write("%f\n" % float(airfoil_coords_dim[i][j][1]))
    
    for i in range(num_nodes_diry):
        for j in range(num_nodes_dirx):
            f.write("%f\n" % airfoil_coords_dim[i][j][2])
    
    f.close()

# Function to dimensionalize coordinates
def dimensionalize_coordinates(nondimensional_coords, leading_edge, chord, twist_angle_rad):
    
    dimensional_coords = []
    for coord in nondimensional_coords:
        x_dimensional = leading_edge[0] + coord[0] * chord
        y_dimensional = leading_edge[1] 
        z_dimensional = leading_edge[2] + coord[1] * chord

        # Apply the twist to the coordinates
        x_dimensional, z_dimensional = apply_twist(x_dimensional, z_dimensional, twist_angle_rad)

        dimensional_coords.append([x_dimensional, y_dimensional, z_dimensional])
    return dimensional_coords

def calculate_twist_angle(leading_edge, trailing_edge):
    dx = trailing_edge[0] - leading_edge[0]
    dy = trailing_edge[1] - leading_edge[1]
    return math.atan2(dy, dx)

def apply_twist(x, y, twist_angle_rad):
    x_rotated = x * math.cos(twist_angle_rad) - y * math.sin(twist_angle_rad)
    y_rotated = x * math.sin(twist_angle_rad) + y * math.cos(twist_angle_rad)
    return x_rotated, y_rotated


import sys

file_path = sys.argv[1] 
bem_data = parse_bem_file(file_path)
print_bem_data(bem_data)
