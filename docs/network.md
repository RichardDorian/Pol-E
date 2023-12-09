# Networking

The robot communicates with the computer using a TCP connection (with the server living on the robot). On boot, the robot will try to connect to the Wi-Fi network specified in the `/flash/wifi.conf` file. If the connection fails the robot will go into error mode and the LED will blink red. If the connection succeeds the LED will be solid green and the code execution will continue. The port that should be used is `7596`.

<details>
<summary>Wifi configuration file example</summary>

<br />

```jsonc
{
  "ssid": "MyWifiNetwork",
  "security": 3, // 0: open, 1: WEP, 2: WPA, 3: WPA2, 4: WPA2_ENT
  "password": "mySuperSecretPassword",
  "timeout": 15000
}
```

</details>

## Packet format

> [!NOTE]
> All packets are sent in **little endian**.

| Field       | Type     | Size (in bytes)                            |
| ----------- | -------- | ------------------------------------------ |
| Packet Size | `UByte`  | `1`                                        |
| Packet ID   | `UByte`  | `1`                                        |
| Data        | `Byte[]` | Value of `Packet Size` - header size (`2`) |

## Packet list

As you can see, the protocol contains a very few amount of packets wich explains why the packet identifier is only a byte.

| ID     | Name       | Description                                               | Direction         |
| ------ | ---------- | --------------------------------------------------------- | ----------------- |
| `0x00` | Reset      | Reset the device                                          | Computer -> Robot |
| `0x01` | Start/Stop | Start/Stop the autonomous behavior                        | Computer -> Robot |
| `0x02` | Sensors    | Sensors (temperature, humidity, pressure & battery level) | Robot -> Computer |

## Packet details

### `0x00` - Reset

**Packet size _(without header)_:**: `0`

### `0x01` - Start/Stop

**Packet size _(without header)_:**: `0`

### `0x02` - Sensors

**Packet size _(without header)_:**: `13`

Battery level does not need to be as precise as the humidity, that's why we chose to send it as an unsigned byte.

| Field         | Description                    | Type    | Size (in bytes) |
| ------------- | ------------------------------ | ------- | --------------- |
| Temperature   | Temperature value (in celcius) | `Float` | `4`             |
| Humidity      | Humidity value (in %)          | `Float` | `4`             |
| Pressure      | Pressure value (in hPa)        | `Float` | `4`             |
| Battery level | Battery level (in %)           | `UByte` | `1`             |
