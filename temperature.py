# ====================================
# RÉGI TESZT VERZIÓ - CSAK KONZOLRA ÍR
# ====================================
# CanSat verzióhoz használd: cansat_main.py
# Teszteléshez használd: test_components.py
# ====================================

from machine import I2C, Pin
import time
import bmp280

# ----- CONFIGURE I2C -----
i2c = I2C(0, scl=Pin(1), sda=Pin(0))  # Change pins to your board
time.sleep(0.2)  # Short delay after power-on

# ----- SCAN FOR I2C DEVICES -----
devices = i2c.scan()
if not devices:
    print("No I2C devices found. Check wiring!")
else:
    print("I2C devices found:", [hex(d) for d in devices])

BMP_ADDR = devices[0] # 0x76=118  # BMP280 address

# ----- CHECK CHIP ID (0xD0 should be 0x58 for BMP280) -----
try:
    chip_id = i2c.readfrom_mem(BMP_ADDR, 0xD0, 1)[0]
    if chip_id != 0x58:
        print("Unexpected chip ID: 0x{:02X}".format(chip_id))
        sensor_alive = False
    else:
        print("BMP280 detected! Chip ID:", hex(chip_id))
        sensor_alive = True
except OSError as e:
    print("Failed to read BMP280 chip ID:", e)
    sensor_alive = False

# ----- INITIALIZE SENSOR -----
sensor = None
if sensor_alive:
    try:
        sensor = bmp280.BMP280(i2c, addr=BMP_ADDR)
        print("BMP280 initialized successfully!")
    except OSError as e:
        print("Failed to initialize BMP280:", e)

# ----- READ TEMPERATURE & PRESSURE LOOP -----
if sensor:
    while True:
        try:
            pres, temp = sensor.read()
            print("Temperature: {:.2f} C, Pressure: {:.2f} hPa".format(temp, pres))
        except OSError as e:
            print("Error reading sensor:", e)
        time.sleep(0.5)
else:
    print("Sensor not ready.")

