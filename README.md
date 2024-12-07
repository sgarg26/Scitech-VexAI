## Vex High Stakes- Scitech Robotics

> [!NOTE] 
> This repo is still early stage.

The V5 code uses the [LemLib template](https://github.com/LemLib/LemLib).

### AI Pipeline

This repo is focused mainly on getting a robot working for the [Vex AI Competition](https://www.vexrobotics.com/v5/competition/vex-ai?srsltid=AfmBOorL4r-guUf88ANdb4c1tMG45PZGn8NL3nQlj_xhJ-_WA2QPJmsj).

The goal is to create a robot that autonomously drives to, and picks up scoring objects. Then it drives to various goals around the field and places objects on the rings. 

Currently, we have a model to identify scoring objects scattered on the field, as well as an occupancy grid for the robot to find paths on. 

We plan on expanding this to being able to plan for multiple objects, as well as find goals. 

### Serial Communication

This solution was inspired by the [Purdue Sigbots Team](https://github.com/BLRSAI).

There have been several unanswered/old topics on Vex Forums regarding serial communication between the V5 and a microcontroller (RPi, Nvidia Jetson, etc). Hopefully our solution can make Sigbots' method a little clearer. 

- A microntroller must be connected to the V5 using a micro-USB cable.
1. Writing from the RPi
    - Serial ports are considered as files in Linux systems, and Python offers the `open` method built-in. `/dev/ttyACM1` can be opened and written to easily.

2. Writing from the V5
    - We were unable to write directly over serial ports from the V5, but we were unsure if this was a C++ limitation or V5 limitation, since it's not a typical Linux system. 
    - Instead, we write to `stdout`, and capture this on the RPi using the [PROS CLI](https://github.com/purduesigbots/pros-cli)

3. Reading from the RPi
    - Once data is posted to the RPi using pros terminal, it's outputted to a file via redirection (`>`).
    - This file can now be processed by Python.

4. Reading from the V5
    - Data written on a serial port gets written to `stdin`, which can just be read by a function like `fgets`. 

### Hardware Used

- We have a Raspberry Pi 5 for all inference tasks, which performs inference in ~150 ms per frame. We use an NCNN model for a good balance between size on disk and inference times. 
- Vex V5 brain controls the robot and we have a serial communication pipeline to send planning information from the Pi to the V5.
