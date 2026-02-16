from machine import I2C, Pin
import time
import bmp280
from microphone_i2s import I2S_Microphone

# ===== KONFIGURÁCIÓ =====

# BMP280 I2C pinok
I2C_SCL = 1
I2C_SDA = 0

# I2S mikrofon pinok (módosítani a bekötésnek megfelelően!)
I2S_SCK = 16   # Bit Clock (BCLK)
I2S_WS = 17    # Word Select (LRCLK/WS)
I2S_SD = 18    # Serial Data (DOUT/SD)

# Mintavételi beállítások
SAMPLE_RATE = 16000  # Hz
BITS = 16            # bit mélység

# Mérési intervallum
SENSOR_INTERVAL = 2.0  # másodperc
MIC_INTERVAL = 0.2     # másodperc


# ===== BMP280 SZENZOR INICIALIZÁLÁSA =====

print("=" * 50)
print("BMP280 + I2S Mikrofon inicializálása")
print("=" * 50)

i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
time.sleep(0.2)

# I2C eszközök keresése
devices = i2c.scan()
if not devices:
    print("❌ Nem találhatók I2C eszközök. Ellenőrizd a bekötést!")
else:
    print("✓ I2C eszközök találva:", [hex(d) for d in devices])

BMP_ADDR = devices[0] if devices else 0x76

# BMP280 inicializálása
sensor = None
try:
    chip_id = i2c.readfrom_mem(BMP_ADDR, 0xD0, 1)[0]
    if chip_id == 0x58:
        print(f"✓ BMP280 észlelve! Chip ID: {hex(chip_id)}")
        sensor = bmp280.BMP280(i2c, addr=BMP_ADDR)
        print("✓ BMP280 sikeresen inicializálva!")
    else:
        print(f"⚠ Váratlan chip ID: {hex(chip_id)}")
except OSError as e:
    print(f"❌ BMP280 hiba: {e}")


# ===== I2S MIKROFON INICIALIZÁLÁSA =====

mic = None
try:
    mic = I2S_Microphone(
        sck_pin=I2S_SCK,
        ws_pin=I2S_WS,
        sd_pin=I2S_SD,
        sample_rate=SAMPLE_RATE,
        bits=BITS
    )
    print("✓ I2S mikrofon sikeresen inicializálva!")
except Exception as e:
    print(f"❌ Mikrofon inicializálási hiba: {e}")


# ===== FŐ PROGRAM LOOP =====

print("\n" + "=" * 50)
print("Mérés indul... (Ctrl+C a leállításhoz)")
print("=" * 50 + "\n")

last_sensor_time = 0
last_mic_time = 0

try:
    while True:
        current_time = time.ticks_ms() / 1000.0

        # BMP280 olvasása
        if sensor and (current_time - last_sensor_time >= SENSOR_INTERVAL):
            try:
                pres, temp = sensor.read()

                # Magasság becslés tengerszint alapján (1013.25 hPa referencia)
                # h = 44330 * (1 - (P/P0)^0.1903)
                altitude = 44330 * (1 - (pres / 1013.25) ** 0.1903)

                print(f"🌡️  Hőmérséklet: {temp:.2f} °C")
                print(f"📊 Légnyomás:   {pres:.2f} hPa")
                print(f"⛰️  Magasság:    {altitude:.1f} m (becsült)")

            except OSError as e:
                print(f"❌ Szenzor olvasási hiba: {e}")

            last_sensor_time = current_time

        # Mikrofon olvasása
        if mic and (current_time - last_mic_time >= MIC_INTERVAL):
            try:
                rms = mic.get_rms_level(256)

                # Vizuális kijelzés
                bar_length = int(rms * 40)
                bar = "█" * bar_length
                print(f"🎤 Hangerő: [{bar:<40}] {rms:.3f}")

            except Exception as e:
                print(f"❌ Mikrofon olvasási hiba: {e}")

            last_mic_time = current_time

        time.sleep(0.05)  # Kis várakozás a CPU terhelés csökkentésére

except KeyboardInterrupt:
    print("\n\n" + "=" * 50)
    print("Leállítás...")
    print("=" * 50)

    if mic:
        mic.deinit()

    print("Program befejezve.")
