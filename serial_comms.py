import time
import os
import numpy as np
from skimage.graph import MCP_Geometric, route_through_array
import json


# Constants indicating if a message was sent from the
# brain or the jetson
BRAIN_IDENTIFIER = "B"
JETSON_IDENTIFIER = "J"

previous_data_received = []
data_received = []

resolution = 1
field_size = 144 # in
grid_size = field_size // resolution

occupancy_grid = np.zeros((grid_size, grid_size), dtype=int)

leg_positions = [
    (72, 48),
    (48, 72),
    (72, 96),
    (96, 72)
]

for leg_position in leg_positions:
    x, y = leg_position
    x_cell = x // resolution
    y_cell = y // resolution
    occupancy_grid[y_cell, x_cell] = 1

# Define the radius of the leg in grid cells
leg_radius = 5

# Mark the area taken up by each leg in the occupancy grid
for leg_position in leg_positions:
    x, y = leg_position
    x_cell = x // resolution
    y_cell = y // resolution
    for i in range(-leg_radius, leg_radius + 1):
        for j in range(-leg_radius, leg_radius + 1):
            if 0 <= x_cell + i < grid_size and 0 <= y_cell + j < grid_size:
                occupancy_grid[y_cell + j, x_cell + i] = 1

# cost map for grid
input_cost_grid = np.ones((grid_size, grid_size), dtype=float)
input_cost_grid[occupancy_grid == 1] = np.inf

path = route_through_array(input_cost_grid, (0, 0), (60, 60))
real_path = np.array(path[0])
real_path = real_path*resolution

path2 = route_through_array(input_cost_grid, (60, 60), (30, 94))
real_path2 = np.array(path2[0])
real_path2 = real_path2*resolution

s = json.dumps(real_path.tolist())
s2 = json.dumps(real_path2.tolist())
# print(s)
# Loads in the model and weights


def write_to_brain(str):
    # Open up serial port and send string to
    # jetson with JETSON_IDENTIFIER
    str = str + "\n"
    print("entered func")
    # ACM1 is used for linux systems. This won't work
    # with Mac or Windows systems.
    f = open("/dev/ttyACM1", "w")
    print("opened vex file")
    f.write(str)
    print("written")
    f.close()


def read_from_brain():
    # Read data from brain

    f = open("brain_output", "r")

    global previous_data_received

    # Read the last line in the brain_output buffer
    data_received = f.readlines()[-1].rstrip().split()

    # If the data is unique, this means the brain is sending
    # new data
    if previous_data_received != data_received:
        print(data_received)
        previous_data_received = data_received
        return True, data_received

    return False, data_received


def main():
    i = 0
    time.sleep(0.5)
    f = open("testfile", "a+")
    print("-----", file=f)
    # print(real_path)

    while True:
        try:
            write_to_brain(s)
            i = input("enter")
            write_to_brain(s2)
            time.sleep(1)
            break

            # output indicates wether or not to output the calculated
            # result to the brain
            # data recieved has the data we need to pass into our reinforcement
            # learning model
            output, data_received = read_from_brain()

            # Converts items in the list of paramaters to floats
            # removes BRAIN_IDENTIFIER
            data_received = [float(x) for x in data_received[1:-1]]

            # Detect all rings in frame, add closest 10 ring
            # positions to the rest of the data we recieved
            # from the brain

            # Debugging/logging
            print(data_received)
            print(data_received, file=f)

            # Time normailization
            data_received[0] = data_received[0] / 105

            # Run an inference on the reinforcement learning model
            # to find which way to move

            # Logging

            # Logging

            # If this data is unique, send the results to the
            # brain
            if output:
                string_to_send = "Return string for vex!"
                write_to_brain(string_to_send)
                i += 1

        # Ctrl + C on this program closes the entire pipeline
        except KeyboardInterrupt:
            print("Closing and Cleaning up...")
            exit()


if __name__ == "__main__":
    main()
