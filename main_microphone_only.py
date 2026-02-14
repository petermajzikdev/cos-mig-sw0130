from machine import Pin
import time
from microphone_i2s import I2S_Microphone

# ===== KONFIGURÁCIÓ =====

# I2S mikrofon pinok
I2S_SCK = 16   # Bit Clock (BCLK)
I2S_WS = 17    # Word Select (LRCLK/WS)
I2S_SD = 18    # Serial Data (DOUT/SD)

# Mintavételi beállítások
SAMPLE_RATE = 16000  # Hz
BITS = 16            # bit mélység

# Mérési intervallum
MIC_INTERVAL = 0.1   # másodperc (100ms frissítés)

# ===== I2S MIKROFON INICIALIZÁLÁSA =====

print("=" * 50)
print("I2S Mikrofon teszt")
print("=" * 50)

mic = None
try:
    mic = I2S_Microphone(
        sck_pin=I2S_SCK,
        ws_pin=I2S_WS,
        sd_pin=I2S_SD,
        sample_rate=SAMPLE_RATE,
        bits=BITS
    )
    if mic.initialized:
        print("OK - I2S mikrofon sikeresen inicializalva!")
        print(f"Mintavetel: {SAMPLE_RATE} Hz, {BITS} bit")
    else:
        print("HIBA - Mikrofon nem inicializalhato!")
except Exception as e:
    print(f"HIBA - Mikrofon inicializalasi hiba: {e}")
    mic = None

# ===== FŐ PROGRAM LOOP =====

if mic and mic.initialized:
    print("\n" + "=" * 50)
    print("Meres indul... (Ctrl+C a leallitashoz)")
    print("=" * 50 + "\n")

    last_mic_time = 0

    try:
        while True:
            current_time = time.ticks_ms() / 1000.0

            # Mikrofon olvasása
            if (current_time - last_mic_time >= MIC_INTERVAL):
                try:
                    rms = mic.get_rms_level(512)

                    # Vizuális kijelzés
                    bar_length = int(rms * 50)
                    bar = "#" * bar_length

                    # Százalékos érték
                    percent = rms * 100

                    print(f"Hangero: [{bar:<50}] {percent:5.1f}%  (RMS: {rms:.4f})")

                except Exception as e:
                    print(f"HIBA - Mikrofon olvasasi hiba: {e}")

                last_mic_time = current_time

            time.sleep(0.02)  # 20ms várakozás

    except KeyboardInterrupt:
        print("\n\n" + "=" * 50)
        print("Leallitas...")
        print("=" * 50)

        mic.deinit()
        print("Program befejeződve.")

else:
    print("\nMikrofon nem mukodik - ellenorizd a bekotest!")
    print("BCLK: GPIO 16")
    print("WS:   GPIO 17")
    print("SD:   GPIO 18")
    print("VCC:  3.3V")
    print("GND:  GND")
