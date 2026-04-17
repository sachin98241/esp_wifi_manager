# Example: Basic usage of ESP32 WiFi Config
from esp32_config import ESP32WiFiConfig

# Initialize WiFi manager
wifi = ESP32WiFiConfig(
    ap_name="ESP32_Config",      # Access point name
    ap_pass="12345678"           # Access point password
)

# Start the WiFi manager
# - First tries saved WiFi
# - If fails, starts AP mode with web interface
wifi.start()
