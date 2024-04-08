# Pol-E

Pol-E is the name of a friendly robot designed to move around and collect data. A real time view of the collected data available on a web dashboard that communicates wirelessly with the robot.

> [!CAUTION]
> This project is in a working state. It is not polished and may contain bugs. It will **not** be finished or maintained. Unfortunately, we didn't have the time to implement every feature we wanted to. This repository is meant to be an archive of the source code for future reference if needed.

## Why?

During the first semester of my first year at Polytech (a French engineering school), I had to work on a project. This project is meant to be a way to learn and apply knowledge in electronics, programming and mechanics. This repository contains the source code of the project, thus only the programming part.

They were some constraints to respect:

- It must be able to move around by itself and avoid obstacles
- It must collect data using the sensors (temperature, humidity, pressure, and optionally ambient light) and write them to the SD card.

> [!NOTE]  
> We had other constraints, but it doesn't not concern the programming part.

## What about the hardware?

The robot was based on a [PyCom](https://docs.pycom.io). This board lets us write Python code to interact with the hardware. The developers behind the board made an API that gives us access to some low-level functions. This API lets us gather data from the sensors, control the motors, and play around with the network.

> [!NOTE]  
> We did not choose the hardware, it was imposed by the teachers.

## Let's do more!

My team and I decided to do more so we could stand out from the others. While reading the specifications of the board we discovered that it was possible to connect to a WiFi network. We thought it would be cool to have a dashboard that displays the data collected by the robot in real-time. So we did it!

Upon start-up, the robot connects to a Wi-Fi network set in the configuration file. It then hosts a TCP server that accepts connections and sends the data to the client. Afterwards, we wrote a simple web server using NodeJS that connects to the TCP server and displays the data on a web page in real time using [WebSockets](https://developer.mozilla.org/docs/Web/API/WebSockets_API).

## Other things I wanted to mention

### The libraries provided by the school

As some of the students were not going to choose computer science as their main field of study, the teacher decided to abstract some of the low level code required to control the hardware (motors, sensors, I2C, etc). This is a good idea as it simplifies the process a lot for those students and removes potential hours of struggle. As a student who is going to choose computer science, I figured that it would be cool to understand how they worked. After some digging and investigation, I decided to rewrite them from scratch. This was a good exercise and I learned a lot (especially on the I2C protocol).

Therefore, the libraries in the lib folder are made by me and are not the ones provided by the school. The libraries provided by the school are not being used in the project and are not included in the source code (I don't own them anyway).

### Multi-threading

We faced a pretty big issue. Python is not a multi-threading language. This is usually not a big deal, but in our case it was. For example, the time it took to measure the distance between the robot and a potential obstacle can be long. Thus, whenever we measure the distance, the robot is unable to react (control the motors, send data through the network). Not to mention that sending data through the network adds more blocking time. We had to find a way and we decided to use the `_thread` module. This module lets us create "threads" and execute a bit more code in parallel.

As a result, we split the code into multiple threads that run in parallel. Each thread has its own file that can be found in the `tasks` folder. The entry point (`main.py`) is responsible for starting the threads and keeping the main thread alive for as long as the robot is active.

In the end, our robot was capable of doing things the others couldn't do. Our robot was able to write to the SD card, check for its surroundings, move around, send data to the dashboard and process all of that at the _same time_.
