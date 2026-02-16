"""
Komponens Teszt Script
Egyenként teszteli a CanSat komponenseket
"""
"""A machine modulból importálja az I2C (kommunikációs protokoll) és Pin (GPIO lábak kezelése) osztályokat"""
from machine import I2C, Pin
"""Időkezelő függvények importálása (várakozás, időmérés)"""
import time
"""Külső config fájl betöltése, ami a pin számokat és beállításokat tartalmazza"""
import config

def test_bmp280():
    """BMP280 szenzor tesztelése"""
    print("\n=== BMP280 TESZT ===")
    try:
        """A BMP280 szenzor driver könyvtár betöltése"""
        import bmp280
        """Létrehozza az I2C busz objektumot"""
        """0 = I2C0 busz használata"""
        """scl=Pin(...) = órajel (clock) láb beállítása a config-ból"""
        """sda=Pin(...) = adat (data) láb beállítása"""
        """freq=... = kommunikációs frekvencia beállítása"""
        i2c = I2C(0, scl=Pin(config.I2C_SCL), sda=Pin(config.I2C_SDA), freq=config.I2C_FREQ)
        """Az I2C busz stabilizálódására vár"""
        time.sleep_ms(100)  

        """Végigpásztázza az I2C buszt, megkeresi az összes csatlakoztatott eszközt"""
        devices = i2c.scan() 
        """Kiírja az eszközök címeit hexadecimális formában (pl. 0x76, 0x77)"""
        print(f"I2C eszközök: {[hex(d) for d in devices]}")

        """Ha nincs eszköz a buszon, hibaüzenetet ír és False-szal tér vissza"""
        if not devices:
            print("❌ Nincs I2C eszköz!")
            return False

        """bmp_addr: Az első talált eszköz címét eltárolja"""
        bmp_addr = devices[0]
        """chip_id olvasás: A 0xD0 memóriacímről olvas 1 byte-ot (ez a chip azonosító regiszter)"""
        chip_id = i2c.readfrom_mem(bmp_addr, 0xD0, 1)[0]
        """Kiírja a chip ID-t hex formában"""
        print(f"Chip ID: {hex(chip_id)}")

        """Ellenőrzi, hogy a chip ID 0x58-e (ez a BMP280 azonosítója)"""
        if chip_id == 0x58:
            """Ha igen, létrehozza a BMP280 szenzor objektumot"""
            sensor = bmp280.BMP280(i2c, addr=bmp_addr)
            """Sikeres inicializálás üzenet"""
            print("✓ BMP280 inicializálva")

            # Teszt olvasások
            """3 mérést végez (0, 1, 2 indexekkel)"""
            for i in range(3):
                """sensor.read(): Beolvassa a nyomást (hPa) és hőmérsékletet (°C)"""
                pres, temp = sensor.read()
                """Magasság számítás: Barometrikus képlettel számol (tengerszint feletti magasság)"""
                """44330 = konstans"""
                """1013.25 = tengerszinti átlagnyomás hPa-ban"""
                """0.1903 = exponens a képletben"""
                altitude = 44330 * (1 - (pres / 1013.25) ** 0.1903)
                """Kiírja az értékeket formázva (2 tizedesjegy temp/nyomás, 1 magasság)"""
                print(f"  [{i+1}] Hőmérséklet: {temp:.2f} °C, Nyomás: {pres:.2f} hPa, Magasság: {altitude:.1f} m")
                """0.5 mp várakozás mérések között"""
                time.sleep(0.5)
            """Ha minden rendben: OK üzenet, True visszatérés"""
            print("✓ BMP280 OK")
            return True
        else:
            """Ha nem 0x58 a chip ID: hiba, False visszatérés"""
            print(f"❌ Ismeretlen chip: {hex(chip_id)}")
            return False
    
    except Exception as e: # Hibakezelés
        print(f"❌ BMP280 hiba: {e}")
        return False


def test_i2s_microphone():
    """I2S mikrofon tesztelése"""
    print("\n=== I2S MIKROFON TESZT ===")
    try:
        """Importálja az I2S mikrofon driver osztályt"""
        from microphone_i2s import I2S_Microphone
        """
        Mikrofon objektum létrehozása az alábbi paraméterekkel:
            sck_pin = Serial Clock (órajel)
            ws_pin = Word Select (bal/jobb csatorna választás)
            sd_pin = Serial Data (adat láb)
            sample_rate = mintavételi frekvencia (pl. 16000 Hz)
            bits = bit mélység (pl. 16 bit)
        """
        mic = I2S_Microphone(
            sck_pin=config.I2S_SCK,
            ws_pin=config.I2S_WS,
            sd_pin=config.I2S_SD,
            sample_rate=config.MIC_SAMPLE_RATE,
            bits=config.MIC_BITS
        )

        if not mic.initialized: # Ellenőrzi az inicializálás sikerességét
            print("❌ I2S mikrofon inicializálás sikertelen")
            return False

        print("✓ I2S mikrofon inicializálva")

        # Teszt olvasások
        print("Hangfelvétel teszt (3 mérés)...")
        for i in range(3):
            """RMS (Root Mean Square) hangerő szintet mér
            Ez egy átlagos hangerősség érték"""
            rms = mic.get_rms_level(config.MIC_SAMPLE_COUNT)
            """Vizuális megjelenítés:
            bar_length = az RMS értéket 40-szeresére skálázza (vizualizációhoz)
            bar = "█" karakterekből készít egy sávot (minél hangosabb, annál hosszabb)
            {bar:<40} = balra igazítva, 40 karakter széles mezőben"""
            bar_length = int(rms * 40)
            bar = "█" * bar_length
            print(f"  [{i+1}] RMS: {rms:.4f} [{bar:<40}]")
            time.sleep(0.5) # 0.5 mp várakozás mérések között
        """Mikrofon leállítása (erőforrások felszabadítása)"""
        mic.deinit()
        print("✓ I2S mikrofon OK")
        return True

    except Exception as e:
        print(f"❌ I2S mikrofon hiba: {e}")
        return False


def test_lora():
    """LoRa modul tesztelése"""
    """LoRa (nagy hatótávú rádió) teszt
"""
    print("\n=== LoRa MODUL TESZT ===")
    try:
        from lora_radio import LoRaRadio
"""LoRa objektum létrehozása SPI pin-ekkel:
sck = Serial Clock
mosi = Master Out Slave In (adat kimenet)
miso = Master In Slave Out (adat bemenet)
cs = Chip Select (eszköz választás)
rst = Reset (újraindítás)
dio0 = Digital I/O 0 (megszakítás kezelés)"""
        lora = LoRaRadio(
            sck_pin=config.LORA_SCK,
            mosi_pin=config.LORA_MOSI,
            miso_pin=config.LORA_MISO,
            cs_pin=config.LORA_CS,
            rst_pin=config.LORA_RST,
            dio0_pin=config.LORA_DIO0
        )
"""LoRa inicializálás rádió paraméterekkel:
frequency = frekvencia MHz-ben (pl. 433 vagy 868 MHz)
tx_power = adóteljesítmény dBm-ben
spreading_factor = terjedési faktor (hatótáv vs sebesség)
bandwidth = sávszélesség
coding_rate = hibavédelem mértéke"""
        if not lora.init(
            frequency=config.LORA_FREQUENCY,
            tx_power=config.LORA_TX_POWER,
            spreading_factor=config.LORA_SPREADING_FACTOR,
            bandwidth=config.LORA_BANDWIDTH,
            coding_rate=config.LORA_CODING_RATE
        ):
            print("❌ LoRa inicializálás sikertelen")
            return False

        print("✓ LoRa modul inicializálva")
        print(f"  Frekvencia: {config.LORA_FREQUENCY} MHz")
        print(f"  TX teljesítmény: {config.LORA_TX_POWER} dBm")

        # Teszt üzenet küldése
        print("Teszt üzenet küldése...")
"""Teszt üzenet összeállítása CSV formátumban (teszt adatok)"""
        test_msg = "TEST,1,25.5,1013.25,100.0,0.1234"

        if lora.send(test_msg):
            print("✓ Teszt üzenet elküldve")
        else:
            print("❌ Küldési hiba")
            return False

        print("✓ LoRa modul OK")
        return True

    except Exception as e:
        print(f"❌ LoRa hiba: {e}")
        return False


def test_sd_card():
    """SD kártya tesztelése"""
    print("\n=== SD KÁRTYA TESZT ===")
    try:
        from sd_logger import SDLogger
        """SD kártya objektum SPI kommunikációval"""
        sd = SDLogger(
            sck_pin=config.SD_SCK,
            mosi_pin=config.SD_MOSI,
            miso_pin=config.SD_MISO,
            cs_pin=config.SD_CS
        )

        if not sd.mount():
            print("❌ SD kártya csatolás sikertelen")
            return False

        print("✓ SD kártya csatolva")

        # Teszt fájl írása
        test_file = "/sd/test_log.txt"
        print(f"Teszt fájl írása: {test_file}")

        try:
            with open(test_file, 'w') as f:
                f.write("CanSat Test Log\n")
                f.write(f"Time: {time.time()}\n")
                f.write("Status: OK\n")

            print("✓ Fájl írás OK")

            with open(test_file, 'r') as f:
                content = f.read()
                print(f"Fájl tartalma:\n{content}")

            print("✓ Fájl olvasás OK")

        except Exception as e:
            print(f"❌ Fájl művelet hiba: {e}")
            return False

        sd.unmount()
        print("✓ SD kártya OK")
        return True

    except Exception as e:
        print(f"❌ SD kártya hiba: {e}")
        return False


def test_leds():
    """LED-ek tesztelése"""
    print("\n=== LED TESZT ===")
    try:
        from led_controller import LEDController

        led = LEDController(config.LED_STATUS_GREEN, config.LED_ERROR_RED)

        print("Zöld LED teszt...")
        led.status_on()
        time.sleep(0.5)
        led.status_off()
        time.sleep(0.5)

        print("Piros LED teszt...")
        led.error_on()
        time.sleep(0.5)
        led.error_off()
        time.sleep(0.5)

        print("Villogás teszt...")
        led.error_blink(3, 200)

        print("✓ LED-ek OK")
        return True

    except Exception as e:
        print(f"❌ LED hiba: {e}")
        return False


def main():
    """Főprogram - összes komponens tesztelése"""
    print("=" * 60)
    print("CanSat KOMPONENS TESZT")
    print("=" * 60)

    results = {
        'LED': test_leds(),
        'BMP280': test_bmp280(),
        'I2S Mikrofon': test_i2s_microphone(),
        'LoRa': test_lora(),
        'SD Kártya': test_sd_card()
    }

    print("\n" + "=" * 60)
    print("ÖSSZEGZÉS")
    print("=" * 60)

    for component, result in results.items():
        status = "✓ OK" if result else "❌ HIBA"
        print(f"{component:15} : {status}")

    print("=" * 60)

    all_ok = all(results.values())
    if all_ok:
        print("✓ MINDEN KOMPONENS MŰKÖDIK")
    else:
        print("⚠ VAN HIBÁS KOMPONENS - ELLENŐRIZD A BEKÖTÉST")

    print("=" * 60)


if __name__ == "__main__":
    main()
