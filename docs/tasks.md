Tasks:

- `network.py` | Network management (Connects to the HTTP server)
- `odometry.py` | Odometry management (Communicates with DRV8833 and sends odometry data to the server with the network thread)
- `movement.py` | Autonomeous/Overriden Movement management (Communicates with DRV8833. If override mode is enabled, network sends movement commands to this)
- `sensors.py` | Sensors management (Communicates with the sensors and sends data to the server and data thread)
- `data.py` | Data management (Stores data from the sensors to the SD card)
