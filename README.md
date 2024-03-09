# Remote Observation and Measurement Vehicle ver. 0

This repository serves as the archive for my engineering thesis project.

The project involves building a very simple and very basic remote controlled unmanned ground vehicle with a camera and a set of environmental sensors, and an accompanying remote control desktop app.
The frame of the vehicle is based on a cheap high-performance off-road RC toy car model. Its systems consist of a primitive microcontroller-based motor control system and a single board computer that serves as the central on-board computer, which is responsible for communications and measurements.

The software consists of three main pieces written either in Python or using the Arduino software stack:

  1. Microcontroller firmware.
  2. On-board computer software.
  3. Remote control app.

I used libraries and/or modules like Qt, OpenCV, Adafruit CircuitPython, PIL, gpiod, numpy, socket, pysierial, psutil and some other parts of the Python standard library. In addition, several Linux programs, such as GStreamer, Hostapd, udhcpd and crontab, were used.

The main purpose of this project was educational, since the project encompasses topics from outside my main field of study.

I am aware of the fact that this project is, lightly speaking, sub-optimal (or rather objectively terrible), however it is the best that I was able to do while being short on time - within a month or two - and learning from scratch.

The ideal solution would've been to use the C/C++ programming languages with dedicated libraries like ROS, STM32 HAL / AVR LibC and Linux kernel libraries, while also utilizing more adequate protocols, such as UDP and RTSP, and also more adequate hardware.

Future improvements are planned as my next private project (that's why this repository is marked as "version 0").

The images below present my work.

---
> ![IMG_20240123_012133_2](https://github.com/infinite-dark/remote-observation-measurement-vehicle-000/assets/126886852/348ca260-25ed-4e4e-be9e-30f640f9c87b)
>
> Figure 1: The assembled PCB of the carrier board for the motor control system.
---
> ![IMG_20240216_220004_2](https://github.com/infinite-dark/remote-observation-measurement-vehicle-000/assets/126886852/4179c96f-0cf2-4594-9827-4ae7b9db002c)
>
> Figure 2: The assembled PCB of the sensor carrier board in the form of a HAT for the SBC.
---
> ![Screenshot from 2024-02-23 22-33-47](https://github.com/infinite-dark/remote-observation-measurement-vehicle-000/assets/126886852/6cba519c-004c-4743-aa75-0519cf587f6d)
>
> Figure 3: The remote control desktop app.
---
> ![IMG20240201221714c_2](https://github.com/infinite-dark/remote-observation-measurement-vehicle-000/assets/126886852/c7808c89-b5fb-4214-b873-569a81298815)
>
> Figure 4: The finished vehicle.
---
