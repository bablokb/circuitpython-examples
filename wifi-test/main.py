import time
import wifi

from secrets import secrets

print(f"My MAC address: {[hex(i) for i in wifi.radio.mac_address]}")

print("Available WiFi networks:")
for network in wifi.radio.start_scanning_networks():
    print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
                                             network.rssi, network.channel))
wifi.radio.stop_scanning_networks()

wifi.radio.connect(secrets.ssid,
                   secrets.password,
                   channel = secrets.channel,
                   timeout = secrets.timeout
                   )
if wifi.radio.connected:
  print(f"connected to {secrets.ssid}")
else:
  print("connection failed")

while True:
  time.sleep(1)
