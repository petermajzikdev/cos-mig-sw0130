"""
CanSat Főprogram
Hőmérséklet, légnyomás, magasság és audio telemetria
"""

from machine import I2C, Pin
import time
import config
import bmp280
from microphone_i2s import I2S_Microphone
from led_controller import LEDController
from sd_logger import SDLogger
from lora_radio import LoRaRadio

# ===== GLOBÁLIS VÁLTOZÓK =====
packet_counter = 0
mission_time = 0
start_time = 0

# ===== INICIALIZÁLÁS =====

def init_system():
    """Rendszer inicializálása"""
    global start_time

    # LED vezérlő
    led = LEDController(config.LED_STATUS_GREEN, config.LED_ERROR_RED)
    led.status_on()

    # BMP280 szenzor
    sensor = None
    try:
        i2c = I2C(0, scl=Pin(config.I2C_SCL), sda=Pin(config.I2C_SDA), freq=config.I2C_FREQ)
        time.sleep_ms(100)

        devices = i2c.scan()
        if devices:
            bmp_addr = devices[0]
            chip_id = i2c.readfrom_mem(bmp_addr, 0xD0, 1)[0]
            if chip_id == 0x58:
                sensor = bmp280.BMP280(i2c, addr=bmp_addr)
    except:
        led.error_blink(3)

    # I2S Mikrofon
    mic = I2S_Microphone(
        sck_pin=config.I2S_SCK,
        ws_pin=config.I2S_WS,
        sd_pin=config.I2S_SD,
        sample_rate=config.MIC_SAMPLE_RATE,
        bits=config.MIC_BITS
    )

    if not mic.initialized:
        led.error_blink(3)

    # LoRa rádió
    lora = LoRaRadio(
        sck_pin=config.LORA_SCK,
        mosi_pin=config.LORA_MOSI,
        miso_pin=config.LORA_MISO,
        cs_pin=config.LORA_CS,
        rst_pin=config.LORA_RST,
        dio0_pin=config.LORA_DIO0
    )

    if not lora.init(
        frequency=config.LORA_FREQUENCY,
        tx_power=config.LORA_TX_POWER,
        spreading_factor=config.LORA_SPREADING_FACTOR,
        bandwidth=config.LORA_BANDWIDTH,
        coding_rate=config.LORA_CODING_RATE
    ):
        led.error_blink(3)

    # SD kártya
    sd = SDLogger(
        sck_pin=config.SD_SCK,
        mosi_pin=config.SD_MOSI,
        miso_pin=config.SD_MISO,
        cs_pin=config.SD_CS
    )

    if sd.mount():
        sd.write_header(config.LOG_FILENAME)
    else:
        led.error_blink(2)

    start_time = time.ticks_ms()

    return led, sensor, mic, lora, sd


def read_sensors(sensor, mic):
    """
    Szenzorok olvasása

    Returns:
        tuple: (temperature, pressure, altitude, audio_rms) vagy None hiba esetén
    """
    try:
        # BMP280 olvasása
        if sensor:
            pres, temp = sensor.read()
            # Magasság számítás
            altitude = 44330 * (1 - (pres / config.SEA_LEVEL_PRESSURE) ** 0.1903)
        else:
            temp = 0.0
            pres = 0.0
            altitude = 0.0

        # Mikrofon RMS olvasása
        if mic and mic.initialized:
            audio_rms = mic.get_rms_level(config.MIC_SAMPLE_COUNT)
        else:
            audio_rms = 0.0

        return temp, pres, altitude, audio_rms

    except:
        return None


def send_telemetry(lora, led, temp, pres, altitude, audio_rms):
    """
    Telemetria küldése LoRa-n

    Returns:
        bool: Sikeres-e a küldés
    """
    global packet_counter

    packet_counter += 1
    packet_id = (config.MISSION_ID, packet_counter)

    try:
        success = lora.send_telemetry(packet_id, temp, pres, altitude, audio_rms)
        if success:
            led.heartbeat()
        else:
            led.error_blink(1)
        return success
    except:
        led.error_blink(1)
        return False


def log_to_sd(sd, timestamp, temp, pres, altitude, audio_rms):
    """
    Adatok mentése SD kártyára

    Returns:
        bool: Sikeres-e a mentés
    """
    try:
        return sd.append_data(config.LOG_FILENAME, timestamp, temp, pres, altitude, audio_rms)
    except:
        return False


# ===== FŐ PROGRAM =====

def main():
    """Fő program loop"""
    global mission_time

    # Rendszer inicializálása
    led, sensor, mic, lora, sd = init_system()

    # Késleltetés a startra
    time.sleep(2)

    # Fő loop
    last_telemetry_time = 0

    while True:
        try:
            # Időbélyeg
            current_time = time.ticks_ms()
            mission_time = time.ticks_diff(current_time, start_time) / 1000.0

            # Telemetria intervallum ellenőrzése
            if time.ticks_diff(current_time, last_telemetry_time) >= config.TELEMETRY_INTERVAL * 1000:

                # Szenzorok olvasása
                sensor_data = read_sensors(sensor, mic)

                if sensor_data:
                    temp, pres, altitude, audio_rms = sensor_data

                    # LoRa küldés
                    send_telemetry(lora, led, temp, pres, altitude, audio_rms)

                    # SD mentés
                    log_to_sd(sd, mission_time, temp, pres, altitude, audio_rms)

                else:
                    # Szenzor olvasási hiba
                    led.error_blink(1)

                last_telemetry_time = current_time

            # Kis várakozás
            time.sleep_ms(50)

        except Exception as e:
            # Kritikus hiba
            led.error_blink(5)
            time.sleep(1)


# Program indítás
if __name__ == "__main__":
    main()
