import re
import os
import pprint
import math

def parse_wing_geometry(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    
    # Split the data into sections based on the separator
    sections = data.split('########################################')
    
    # Extract the directory path from the first line
    dir_pattern = re.compile(r"Airfoil File Directory,\s*(.+)")
    
    wing_geometries = []
    
    # Define the patterns for extracting data
    patterns = {
        "Airfoil File Name": re.compile(r"Airfoil File Name,\s*(.+)"),
        "Geom Name": re.compile(r"Geom Name,\s*(.+)"),
        "Geom ID": re.compile(r"Geom ID,\s*(.+)"),
        "Airfoil Index": re.compile(r"Airfoil Index,\s*(\d+)"),
        "XSec Flag": re.compile(r"XSec Flag,\s*(\d+)"),
        "XSec Index": re.compile(r"XSec Index,\s*(\d+)", re.MULTILINE),
        "XSecSurf ID": re.compile(r"XSecSurf ID,\s*(.+)", re.MULTILINE),
        "FoilSurf u Value": re.compile(r"FoilSurf u Value,\s*([\d\.]+)"),
        "Global u Value": re.compile(r"Global u Value,\s*([\d\.]+)"),
        "Leading Edge Point": re.compile(r"Leading Edge Point,\s*([\d\.\-]+),\s*([\d\.\-]+),\s*([\d\.\-]+)"),
        "Trailing Edge Point": re.compile(r"Trailing Edge Point,\s*([\d\.\-]+),\s*([\d\.\-]+),\s*([\d\.\-]+)"),
        "Chord": re.compile(r"Chord,\s*([\d\.]+)")
    }
    
    for section in sections[1:]:
        if section.strip():  # Ignore empty sections
            wing_geom = {}
            for key, pattern in patterns.items():
                match = pattern.search(section)
                if match:
                    if key in ["Leading Edge Point", "Trailing Edge Point"]:
                        wing_geom[key] = [float(match.group(1)), float(match.group(2)), float(match.group(3))]
                    elif key in ["Airfoil Index", "XSec Flag", "XSec Index"]:
                        wing_geom[key] = int(match.group(1))
                    else:
                        wing_geom[key] = match.group(1).strip() if key in ["Airfoil File Name", "Geom Name", "Geom ID", "XSecSurf ID"] else float(match.group(1))
            wing_geometries.append(wing_geom)
    
    # if os.path.exists(file_path):
    #     os.remove(file_path)
    # else:
    #     print("The file does not exist")


    
    return wing_geometries

def parse_airfoil_dat(file_path):
    airfoil_coords = []
    with open(file_path, 'r') as file:
        lines = file.readlines()[1:]  # Skip the first line (path or header)
        for line in reversed(lines):
            if line.strip():  # Ignore empty lines
                coords = list(map(float, line.strip().split()))
                airfoil_coords.append(coords)

    del airfoil_coords[int(round(len(airfoil_coords)/2))] # delete multiple leading edge coord

    return airfoil_coords

def combine_wing_and_airfoil_data(wing_geometry_file_path):
    # Parse wing geometry
    wing_geometries = parse_wing_geometry(wing_geometry_file_path)
    
    # Read and attach airfoil data
    for geom in wing_geometries:
        airfoil_file_name = os.path.dirname(wing_geometry_file_path) + "/" + geom["Airfoil File Name"]
        if os.path.exists(airfoil_file_name):
            geom["Airfoil Coordinates"] = parse_airfoil_dat(airfoil_file_name)
        else:
            geom["Airfoil Coordinates"] = []

        # if os.path.exists(airfoil_file_name):
        #     os.remove(airfoil_file_name)
        # else:
        #     print("The file does not exist")    

    return wing_geometries

def print_wing_data(file_path, wing_data, check_symmetry=False):

    # create file
    filename = os.path.basename(file_path).replace(".csv",".x")
    f = open(filename, "w")

    num_blocks = 1

    airfoil_coords_dim = []
    for geom in wing_data:
        airfoil_coords_ndim = geom['Airfoil Coordinates']
        leading_edge = geom['Leading Edge Point']
        trailing_edge = geom['Trailing Edge Point']
        chord = geom['Chord']
        
        airfoil_coords_dim.append(dimensionalize_coordinates(airfoil_coords_ndim, leading_edge, trailing_edge, chord))
    
    num_nodes_dirx = len(wing_data[0]['Airfoil Coordinates'])
    num_nodes_diry = len(wing_data) if check_symmetry == False else 2*len(wing_data) - 1
    
    f.write(f"{num_blocks}\n")
    f.write(f"{num_nodes_dirx}\t{num_nodes_diry}\t{1}\n")

    for i in reversed(range(len(wing_data))):
      for j in range(len(wing_data[0]['Airfoil Coordinates'])):
          f.write("%f\n" % airfoil_coords_dim[i][j][0])
    if check_symmetry:
        for i in range(len(wing_data))[1:]:
            for j in range(len(wing_data[0]['Airfoil Coordinates'])):
                f.write("%f\n" % airfoil_coords_dim[i][j][0])

    for i in reversed(range(len(wing_data))):
      for j in range(len(wing_data[0]['Airfoil Coordinates'])):
          f.write("%f\n" % float(-1.0*airfoil_coords_dim[i][j][2]))
    if check_symmetry:
        for i in range(len(wing_data))[1:]:
            for j in range(len(wing_data[0]['Airfoil Coordinates'])):
                f.write("%f\n" % airfoil_coords_dim[i][j][2])
    
    for i in reversed(range(len(wing_data))):
      for j in range(len(wing_data[0]['Airfoil Coordinates'])):
          f.write("%f\n" % airfoil_coords_dim[i][j][1])
    if check_symmetry:
        for i in range(len(wing_data))[1:]:
            for j in range(len(wing_data[0]['Airfoil Coordinates'])):
                f.write("%f\n" % airfoil_coords_dim[i][j][1])
    
    f.close()

# Function to dimensionalize coordinates
def dimensionalize_coordinates(nondimensional_coords, leading_edge, trailing_edge,chord):
    
    # Calculate the twist angle
    twist_angle_rad = calculate_twist_angle(leading_edge, trailing_edge)
    
    dimensional_coords = []
    for coord in nondimensional_coords:
        x_dimensional = leading_edge[0] + coord[0] * chord
        y_dimensional = leading_edge[2] + coord[1] * chord
        z_dimensional = leading_edge[1]

        # Apply the twist to the coordinates
        x_dimensional, y_dimensional = apply_twist(x_dimensional-leading_edge[0], y_dimensional-leading_edge[2], twist_angle_rad)
        x_dimensional += leading_edge[0]
        y_dimensional += leading_edge[2]

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

# Example usage
import sys

file_path = sys.argv[1] 

flag_symmetry = ""
if len(sys.argv) == 3:
    flag_symmetry = sys.argv[2]

check_symmetry = False
if (flag_symmetry == "-s"):
    check_symmetry = True


wing_geometry_file_path = file_path
wing_data = combine_wing_and_airfoil_data(wing_geometry_file_path)
print_wing_data(file_path, wing_data, check_symmetry)

