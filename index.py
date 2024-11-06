import time
import urequests
from machine import ADC, Pin
import network
import gc

# Constants for solar and battery thresholds
SOLAR_VOLTAGE_THRESHOLD = 5.0  # Example threshold for solar power (in Volts)
BATTERY_VOLTAGE_THRESHOLD = 3.6  # Minimum voltage for battery to power the system

# Blink credentials (replace with your actual Blink credentials)
BLINK_API_URL = "https://api.blinkstick.com/v1/devices/YOUR_DEVICE_ID"
BLINK_API_KEY = "YOUR_BLINK_API_KEY"
BLINK_STATE_ON = {"state": "on"}
BLINK_STATE_OFF = {"state": "off"}

# ESP32 Pin configurations for sensors
SOLAR_PIN = ADC(Pin(34))  # Solar panel voltage sensor connected to GPIO34
BATTERY_PIN = ADC(Pin(35))  # Battery voltage sensor connected to GPIO35

# Calibration for the ADC (e.g., 3.3V reference)
ADC_MAX_VALUE = 4095
VREF = 3.3

def read_voltage(sensor: ADC) -> float:
    """Read and convert the ADC value to a voltage."""
    adc_value = sensor.read()
    return (adc_value / ADC_MAX_VALUE) * VREF

def connect_wifi():
    """Connect to Wi-Fi."""
    ssid = "YOUR_SSID"
    password = "YOUR_PASSWORD"
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    print("Connected to Wi-Fi:", wlan.ifconfig())

def control_blink_light(state):
    """Control the Blink light via Blink API."""
    headers = {
        "Authorization": f"Bearer {BLINK_API_KEY}",
        "Content-Type": "application/json"
    }
    if state == "on":
        response = urequests.put(BLINK_API_URL, json=BLINK_STATE_ON, headers=headers)
    elif state == "off":
        response = urequests.put(BLINK_API_URL, json=BLINK_STATE_OFF, headers=headers)
    else:
        print("Invalid state for Blink light.")
        return

    if response.status_code == 200:
        print(f"Blink light turned {state}.")
    else:
        print(f"Error controlling Blink light: {response.status_code}")

def manage_hybrid_system():
    """Main logic to manage hybrid energy system and Blink light."""
    solar_voltage = read_voltage(SOLAR_PIN)
    battery_voltage = read_voltage(BATTERY_PIN)

    print(f"Solar voltage: {solar_voltage:.2f} V, Battery voltage: {battery_voltage:.2f} V")

    if solar_voltage >= SOLAR_VOLTAGE_THRESHOLD:
        print("Sufficient solar power. Turning on the Blink light.")
        control_blink_light("on")
    elif battery_voltage >= BATTERY_VOLTAGE_THRESHOLD:
        print("Solar power insufficient, but battery is sufficient. Turning on the Blink light.")
        control_blink_light("on")
    else:
        print("Insufficient power from both solar and battery. Turning off the Blink light.")
        control_blink_light("off")

def main():
    """Main entry point for the program."""
    gc.collect()  # Run garbage collection to free memory
    connect_wifi()

    while True:
        manage_hybrid_system()
        time.sleep(60)  # Delay between checks (adjust as needed)

# Run the main function
if __name__ == "__main__":
    main()
