## Vex High Stakes- Scitech Robotics

> [!NOTE] 
> This repo is still early stage.

The V5 code uses the [LemLib template](https://github.com/LemLib/LemLib).

### AI Pipeline

This repo is focused mainly on getting a robot working for the [Vex AI Competition](https://www.vexrobotics.com/v5/competition/vex-ai?srsltid=AfmBOorL4r-guUf88ANdb4c1tMG45PZGn8NL3nQlj_xhJ-_WA2QPJmsj).

The goal is to create a robot that autonomously drives to, and picks up scoring objects. Then it drives to various goals around the field and places objects on the rings. 

Currently, we have a model to identify scoring objects scattered on the field, as well as an occupancy grid for the robot to find paths on. 

We plan on expanding this to being able to plan for multiple objects, as well as find goals. 

### Hardware Used

- We have a Raspberry Pi 5 for all inference tasks, which performs inference in ~150 ms per frame. We use an NCNN model for a good balance between size on disk and inference times. 
- Vex V5 brain controls the robot and we have a serial communication pipeline to send planning information from the Pi to the V5.
