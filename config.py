# CanSat Konfiguráció

# === GPIO PINOUT ===
# BMP280 I2C
I2C_SCL = 1
I2C_SDA = 0
I2C_FREQ = 400000  # 400 kHz

# I2S Mikrofon
I2S_SCK = 35 # BCLK (sárga vezeték)
I2S_WS = 18 # LRCL (narancs vezeték)
I2S_SD = 22 # DOUT (kék vezeték)

# LoRa SPI (RFM95W / SX1276 / SX1278)
LORA_SCK = 10
LORA_MOSI = 11
LORA_MISO = 12
LORA_CS = 13
LORA_RST = 14
LORA_DIO0 = 15

# SD kártya SPI
SD_SCK = 2
SD_MOSI = 3
SD_MISO = 4
SD_CS = 5

# LED indikátorok
LED_STATUS_GREEN = 20  # Zöld LED - normál működés
LED_ERROR_RED = 21     # Piros LED - hiba jelzés

# === SZENZOROK ===
BMP280_ADDR = 0x76

# === I2S MIKROFON ===
MIC_SAMPLE_RATE = 8000  # Hz (alacsonyabb a sávszélesség miatt)
MIC_BITS = 16
MIC_SAMPLE_COUNT = 128  # Minta darabszám RMS számításhoz

# === TELEMETRIA ===
TELEMETRY_INTERVAL = 1.0  # másodperc (adatküldési gyakoriság)
SEA_LEVEL_PRESSURE = 1013.25  # hPa (referencia légnyomás)

# === SD KÁRTYA ===
LOG_FILENAME = "/sd/cansat_log.csv"
SD_BUFFER_SIZE = 5  # Hány mérés után írjon SD-re

# === LoRa BEÁLLÍTÁSOK ===
LORA_FREQUENCY = 868.0  # MHz (Európa: 868 MHz, USA: 915 MHz)
LORA_TX_POWER = 14  # dBm (5-20)
LORA_BANDWIDTH = 125000  # Hz
LORA_SPREADING_FACTOR = 7  # 7-12 (nagyobb = nagyobb hatótáv, de lassabb)
LORA_CODING_RATE = 5  # 5-8

# === EGYÉB ===
MISSION_ID = "COSMIG2026"  # Azonosító
