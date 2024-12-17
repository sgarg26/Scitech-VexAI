import time
import numpy as np
from skimage.graph import route_through_array
from ultralytics import YOLO
import json
import pyrealsense2 as rs

cur_pos = (5, 10) # we assume bot starts at 0, 0 always. Position should be updated over time.

model = YOLO("./model_training/best_ncnn_model")

pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

def get_center(bbox):
    x1, y1, x2, y2, = bbox
    cx = int((x1+x2) / 2)
    cy = int((y1+y2) / 2)
    return cx, cy

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


# cost map for grid
input_cost_grid = np.ones((grid_size, grid_size), dtype=float)
input_cost_grid[occupancy_grid == 1] = np.inf

def get_shortest_path(start, end):
    path = route_through_array(input_cost_grid, start, end)
    real_path = np.array(path[0])
    real_path = real_path*resolution
    s = json.dumps(real_path.tolist())
    return s

def conv_to_in(pos):
    return pos * 39.3701

def write_to_brain(str):
    # Open up serial port and send string to
    # jetson with JETSON_IDENTIFIER
    str = str + "\n"
    print("Writing to v5")
    # ACM1 is used for linux systems. This won't work
    # with Mac or Windows systems.
    f = open("/dev/ttyACM1", "w")
    f.write(str)
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
    try:
        s = None
        found_something = False
        while True:
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
            if not depth_frame or not color_frame: continue

            # depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            x, y, z = (0, 0, 0)
            results = model(color_image)
            for r in results:
                for box in r.boxes:
                    print("found something")
                    
                    b = box.xyxy[0]
                    cx, cy = get_center(b.cpu().numpy())
                    distance = depth_frame.get_distance(cx, cy)
                    if not distance > 0:
                        continue
                    found_something = True
                    x, y, z = rs.rs2_deproject_pixel_to_point(depth_intrinsics, [cx, cy], distance)
                    print(x, y, z)
                    end = (int(np.round(cur_pos[0]+conv_to_in(x))), int(np.round(cur_pos[1]+conv_to_in(z))))
                    print(end)
                    s = get_shortest_path(cur_pos, np.abs(end))
                    print(s)
                    break # just get the first ring, travel to one ring per iteration.
            # print(x, y, z)
            if found_something: break


        write_to_brain(s)
        time.sleep(1)


        # Ctrl + C on this program closes the entire pipeline
    except KeyboardInterrupt:
        print("Closing and Cleaning up...")
        exit()


if __name__ == "__main__":
    main()
