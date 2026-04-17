import network
import socket
import time


class ESP32WiFiConfig:

    def __init__(self, ap_name="ESP32_Config", ap_pass="12345678"):
        self.ap_name = ap_name
        self.ap_pass = ap_pass
        self.sta = network.WLAN(network.STA_IF)
        self.ap = network.WLAN(network.AP_IF)
        self.server = None

    '''
       # Attempt to connect to a WiFi network.

        Args:
            ssid (str): WiFi network name
            password (str): WiFi network password

        Returns:
            bool: True if connection successful, False otherwise
    '''
    def connect_wifi(self, ssid, password):
        self.sta.active(False)
        time.sleep(1)
        self.sta.active(True)

        print("Connecting to:", ssid)

        try:
            self.sta.connect(ssid, password)
        except Exception as e:
            print("Connect error:", e)
            return False

        for _ in range(10):
            if self.sta.isconnected():
                print("Connected:", self.sta.ifconfig())
                return True
            time.sleep(1)

        print("Connection Failed")
        return False

    """
        # Disconnect from the currently connected WiFi network.

        Returns:
            bool: True if disconnect successful, False otherwise
        """
    def disconnect(self):
        try:
            if self.sta.isconnected():
                self.sta.disconnect()
                self.sta.active(False)
                print("Disconnected from WiFi")
                return True
            else:
                print("Not connected to any WiFi network")
                return False
        except Exception as e:
            print("Disconnect error:", e)
            return False

    #  Saved-credentials helpers

    def load_wifi(self):
        try:
            with open("wifi.txt", "r") as f:
                ssid, password = f.read().split(",")
                return ssid, password
        except:
            return None, None

    def save_wifi(self, ssid, password):
        with open("wifi.txt", "w") as f:
            f.write(ssid + "," + password)

    def clear_wifi(self):
        try:
            import os
            os.remove("wifi.txt")
            print("Saved WiFi deleted")
        except:
            print("No WiFi file")

        if self.sta.isconnected():
            self.sta.disconnect()
            self.sta.active(False)

    #  Scan

    def scan_wifi(self):
        self.sta.active(True)
        self.sta.disconnect()
        time.sleep(1)

        nets = self.sta.scan()
        wifi_list = []

        for net in nets:
            try:
                ssid = net[0].decode()
                rssi = net[3]
                if ssid:
                    wifi_list.append((ssid, rssi))
            except:
                pass

        return wifi_list

    #  Web helpers
    
    def url_decode(self, s):
        res = ""
        i = 0
        while i < len(s):
            if s[i] == '%':
                try:
                    hex_val = s[i + 1:i + 3]
                    res += chr(int(hex_val, 16))
                    i += 3
                except:
                    res += s[i]
                    i += 1
            elif s[i] == '+':
                res += ' '
                i += 1
            else:
                res += s[i]
                i += 1
        return res

    def web_page(self, wifi_list, current_ssid=None):
        status_bar = ""
        if current_ssid:
            status_bar = f"""
<div style="background:#28a745;color:white;padding:10px;border-radius:8px;margin:10px;">
  Connected to: <b>{current_ssid}</b>
  &nbsp;&nbsp;
  <a href="/disconnect" style="color:white;text-decoration:underline;">Disconnect</a>
</div>
"""

        html = """<!DOCTYPE html>
<html>
<head>
<title>ESP32 WiFi Setup</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { font-family: Arial; background: #f2f2f2; text-align: center; }
h2   { color: #333; }
.wifi {
    background: white; margin: 10px; padding: 15px;
    border-radius: 10px; cursor: pointer;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.signal { font-size: 12px; color: gray; }
button {
    padding: 10px 20px; border: none; background: #007BFF;
    color: white; border-radius: 5px; font-size: 16px;
}
input  { padding: 10px; width: 80%; margin-top: 10px; }
#popup {
    display: none; position: fixed; top: 30%; left: 10%; width: 80%;
    background: white; padding: 20px; border-radius: 10px;
    box-shadow: 0 5px 10px rgba(0,0,0,0.3);
}
</style>
<script>
function selectSSID(ssid) {
    document.getElementById("ssid").value = ssid;
    document.getElementById("popup").style.display = "block";
}
function scanWifi()   { window.location.href = "/"; }
function forgetWifi() {
    if (confirm("Forget saved WiFi?")) window.location.href = "/forget";
}
function disconnectWifi() {
    if (confirm("Disconnect from current WiFi?")) window.location.href = "/disconnect";
}
</script>
</head>
<body>
<h2>ESP32 WiFi Setup</h2>
""" + status_bar + """
<button onclick="scanWifi()">Scan</button>
&nbsp;
<button onclick="forgetWifi()" style="background:#dc3545;">🗑 Forget</button>
&nbsp;
<button onclick="disconnectWifi()" style="background:#6c757d;">⏏ Disconnect</button>
<br><br>
"""

        for wifi, rssi in wifi_list:
            html += f'''
<div class="wifi" onclick="selectSSID('{wifi}')">
  <b>{wifi}</b><br>
  <span class="signal">Signal: {rssi} dBm</span>
</div>
'''

        html += """
<div id="popup">
  <h3>Enter Password</h3>
  <form action="/" method="get">
    <input type="hidden" name="ssid" id="ssid">
    <input type="password" name="password" placeholder="Enter Password"><br><br>
    <button type="submit">Connect</button>
    &nbsp;
    <button type="button" onclick="document.getElementById('popup').style.display='none'">Cancel</button>
  </form>
</div>
</body>
</html>
"""
        return html

    def parse_request(self, request):
        try:
            req = request.split(' ')[1]
            if '?' in req:
                params = req.split('?')[1]
                data = {}
                for pair in params.split('&'):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        data[key] = self.url_decode(value)
                return data
        except:
            pass
        return {}

    #  Main — AP + server always running

    def start(self):
        # Try saved WiFi first (but keep the server running regardless)
        ssid, password = self.load_wifi()
        if ssid:
            print("Trying saved WiFi:", ssid)
            self.connect_wifi(ssid, password)   # result is informational only

        # Start AP so the config portal is always reachable
        self.ap.active(True)
        self.ap.config(essid=self.ap_name, password=self.ap_pass)
        print("AP Started  →  http://192.168.4.1")

        # Start HTTP server
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        self.server = socket.socket()
        self.server.bind(addr)
        self.server.listen(1)
        print("Server running...")

        while True:
            try:
                cl, addr = self.server.accept()
                print("Client:", addr)
                request = cl.recv(1024).decode()
                data = self.parse_request(request)

                if "ssid" in data and "password" in data:
                    # --- Connect to new network ---
                    if self.connect_wifi(data["ssid"], data["password"]):
                        self.save_wifi(data["ssid"], data["password"])
                        response = "<h2>Connected & Saved!</h2><a href='/'>Back</a>"
                    else:
                        response = "<h2>Failed to Connect</h2><a href='/'>Back</a>"

                elif "/forget" in request:
                    # --- Forget saved credentials ---
                    self.clear_wifi()
                    response = "<h2>WiFi Forgotten. Restarting portal…</h2><a href='/'>Back</a>"

                elif "/disconnect" in request:
                    # --- Disconnect (keep AP/server alive) ---
                    self.disconnect()
                    response = "<h2>Disconnected from WiFi</h2><a href='/'>Back</a>"

                else:
                    # --- Main page: scan & show networks ---
                    wifi_list = self.scan_wifi()
                    current = self.sta.config('essid') if self.sta.isconnected() else None
                    response = self.web_page(wifi_list, current_ssid=current)

                cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
                cl.send(response)
                cl.close()

            except Exception as e:
                print("Server error:", e)


if __name__ == "__main__":
    mgr = ESP32WiFiConfig()
    mgr.start()          
