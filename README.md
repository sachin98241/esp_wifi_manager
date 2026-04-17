# ESP32 WiFi Config

A lightweight and user-friendly WiFi Manager for ESP32 using MicroPython.
It enables dynamic WiFi configuration via a web portal — similar to how modern IoT devices (like smart plugs, routers, etc.) connect to WiFi.

## Features

- **Web-based setup**: No USB/serial terminal required
- **Access Point mode**: Creates temporary WiFi AP for configuration
- **Signal strength**: Shows RSSI (signal quality) for each network
- **Auto-save**: Remembers WiFi credentials between reboots
- **Mobile-friendly**: Works on phones and tablets
- **Lightweight**: Minimal dependencies (uses built-in network, socket, time)

## Installation

### 1. Method 1: Using mip (Recommended for MicroPython)
```python
import mip
mip.install("github:sachin98241/ESP_WiFi_Manager")
```

### 2. Method 2: As a Python Module (via PyPI)
pip install esp-wifi-manager

### 3. Method 3: Manual Installation
1. Flash MicroPython to your ESP32 
2. Copy `esp32_config.py` to your ESP32
3. Use your favorite MicroPython IDE (Thonny, VS Code + PyMicroPython, etc.)
4. Create `main.py` with the usage code below

### First Time Setup

1. **Power on** your ESP32
2. **Wait 2-3 seconds** for boot
3. **On your phone/computer**, look for WiFi network: `ESP32_Config`
4. **Connect** with password: `12345678`
5. **Open browser** and go to: `http://192.168.4.1`
6. **Select your WiFi** network from the list
7. **Enter password** and click "Connect"
8. **Done!** ESP32 will restart and connect to your WiFi

### Subsequent Startups

- If saved WiFi is available → **Auto-connects** (no AP needed)
- If saved WiFi fails → **Starts AP mode** again (follow setup steps)

Initialize the WiFi manager.

**Parameters:**
- `ap_name` (str): Name of the Access Point (visible when scanning WiFi)
- `ap_pass` (str): Password for the Access Point (8+ characters recommended)

### `wifi.start()`

Start the WiFi manager. This method:
1. Tries to connect to saved WiFi
2. If successful → returns (ESP32 is connected)
3. If fails → starts AP mode with web server (blocks forever until user connects)

## Troubleshooting

### "Can't see ESP32_Config WiFi"
- Ensure ESP32 is powered on
- Wait 5 seconds after power on
- Check if your device supports 2.4GHz WiFi (ESP32 doesn't support 5GHz)
- Try restarting the ESP32

### "Connection failed"
- Double-check the password
- Ensure WiFi is 2.4GHz (not 5GHz)
- Check WiFi signal strength on the page
- Try connecting to a different network

### "Forgotten WiFi - how to reset"
- On the setup page, click "Forget WiFi"
- Device will restart and show AP again
- Or delete `wifi.txt` file if you have file system access

### "Password with special characters doesn't work"
- Use the web interface (recommended)
- Avoid special characters if using serial input
- The web form handles encoding automatically

## How It Works

1. When ESP32 starts: The system tries to load saved WiFi credentials from local storage.
2. If failed → creates Access Point
3. Open browser at:
   http://192.168.4.1
4. When user connects to ESP32 WiFi:
   Opens browser → visits 192.168.4.1
   ESP32 scans nearby WiFi networks
   Displays list of SSIDs with signal strength (RSSI)
5. User selects SSID and provides password and ESP32 attempts connection.

## System Flow:

```text
Power ON
|
▼
Load saved WiFi
|
├──► Connect OK
│ |
│ ▼
│ DONE
│
└──► Connect FAIL
|
▼
Start AP Mode
|
▼
Start Web Server
|
▼
User Inputs WiFi
|
▼
Try Connect Again
```

## Modules & Libraries Used

**network module**: Controls WiFi/AP mode
**socket module**: Creates HTTP server
**time module**: Handles delays and timeouts
**File I/O**: Saves credentials to `wifi.txt`
**URL decoding**: Handles special characters in passwords


## Requirements

* ESP32
* MicroPython firmware
