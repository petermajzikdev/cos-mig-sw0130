# Raspberry Pi Pico Feltöltési Útmutató

## Szükséges fájlok (egyszerű teszt verzió)

A következő 3 fájlt kell feltölteni a Pico-ra:
1. **main.py** - Főprogram
2. **bmp280.py** - BMP280 szenzor driver
3. **microphone_i2s.py** - I2S mikrofon driver

## Thonny beállítása

### 1. MicroPython telepítése a Pico-ra (ha még nincs)

1. Csatlakoztasd a Pico-t USB-vel, miközben nyomva tartod a **BOOTSEL** gombot
2. A Pico megjelenik egy USB meghajtóként
3. Thonny-ban: **Run → Configure interpreter...**
4. Válaszd: **MicroPython (Raspberry Pi Pico)**
5. Kattints: **Install or update MicroPython**
6. Válaszd ki a Pico-t és kattints **Install**

### 2. Interpreter beállítása

1. Thonny-ban: **Run → Configure interpreter...**
2. Válaszd: **MicroPython (Raspberry Pi Pico)**
3. Port: Automatikusan érzékeli (vagy válaszd ki manuálisan)
4. Kattints: **OK**

## Fájlok feltöltése

### Módszer 1: Drag & Drop a Thonny-ban

1. Nyisd meg a Thonny-t
2. Jobb oldalon látnod kell a **Files** panelt
   - Ha nem látod: **View → Files**
3. Felül látszik két mappa:
   - **This computer** (a géped)
   - **Raspberry Pi Pico** (az eszköz)

4. **Töltsd fel a fájlokat egyenként:**
   - Nyisd meg a `bmp280.py` fájlt a Thonny-ban
   - Kattints: **File → Save as...**
   - Válaszd: **Raspberry Pi Pico**
   - Mentsd el ugyanazon néven: `bmp280.py`

   - Nyisd meg a `microphone_i2s.py` fájlt
   - **File → Save as... → Raspberry Pi Pico**
   - Név: `microphone_i2s.py`

   - Nyisd meg a `main.py` fájlt
   - **File → Save as... → Raspberry Pi Pico**
   - Név: `main.py`

### Módszer 2: Files panelből

1. Thonny-ban **View → Files**
2. Felül: **This computer** - navigálj a projekt mappába
3. Jobb klikk a `bmp280.py`-on → **Upload to /**
4. Jobb klikk a `microphone_i2s.py`-on → **Upload to /**
5. Jobb klikk a `main.py`-on → **Upload to /**

## Ellenőrzés

### Feltöltött fájlok ellenőrzése

1. Thonny **Files** panelben kattints a **Raspberry Pi Pico** mappára
2. Látnod kell:
   - `main.py`
   - `bmp280.py`
   - `microphone_i2s.py`

### Program futtatása

1. **Automatikus indítás:** A Pico újraindításakor automatikusan elindul a `main.py`
2. **Manuális futtatás Thonny-ból:**
   - Nyisd meg a `main.py`-t a Pico-ról
   - Kattints a zöld **Run** gombra (F5)

### Kimenet ellenőrzése

A Shell ablakban (Thonny alján) látnod kell:
```
==================================================
BMP280 + I2S Mikrofon inicializálása
==================================================
✓ I2C eszközök találva: ['0x76']
✓ BMP280 észlelve! Chip ID: 0x58
✓ BMP280 sikeresen inicializálva!
✓ I2S mikrofon sikeresen inicializálva!

==================================================
Mérés indul... (Ctrl+C a leállításhoz)
==================================================

🌡️  Hőmérséklet: 23.45 °C
📊 Légnyomás:   1013.25 hPa
⛰️  Magasság:    112.3 m (becsült)
🎤 Hangerő: [████████                                ] 0.234
```

## Leállítás

- **Thonny-ból:** STOP gomb vagy `Ctrl+C`
- **Automatikus indítás letiltása:** Töröld a `main.py` fájlt a Pico-ról

## Hardver bekötés

### BMP280 (I2C)
| BMP280 | Pico     |
|--------|----------|
| VCC    | 3.3V     |
| GND    | GND      |
| SCL    | GPIO 1   |
| SDA    | GPIO 0   |

### I2S MEMS Mikrofon
| Mikrofon | Pico     |
|----------|----------|
| VCC/3V   | 3.3V     |
| GND      | GND      |
| BCLK/SCK | GPIO 16  |
| LRCLK/WS | GPIO 17  |
| DOUT/SD  | GPIO 18  |
| SEL      | GND      |

## Hibaelhárítás

### "Device is busy or does not respond"
- Próbáld újracsatlakoztatni a Pico-t
- Thonny-ban: **Stop/Restart** gomb
- Zárd be és nyisd meg újra a Thonny-t

### "No module named 'bmp280'"
- A `bmp280.py` fájl nincs feltöltve a Pico-ra
- Ellenőrizd a Files panelben

### BMP280 nem észlelhető
- Ellenőrizd a vezetékeket (I2C SCL/SDA)
- Próbáld meg a másik I2C címet (0x77 helyett 0x76)

### I2S mikrofon hibák
- Ellenőrizd a 3.3V tápellátást
- SEL pin bekötése: GND (bal csatorna)
- Ha nem működik, próbáld meg más GPIO pinekkel

## Konfigurációs változtatások

Ha módosítani szeretnéd a PIN bekötéseket, szerkeszd a `main.py` elejét:

```python
# BMP280 I2C pinok
I2C_SCL = 1
I2C_SDA = 0

# I2S mikrofon pinok
I2S_SCK = 16   # Bit Clock (BCLK)
I2S_WS = 17    # Word Select (LRCLK/WS)
I2S_SD = 18    # Serial Data (DOUT/SD)

# Mintavételi beállítások
SAMPLE_RATE = 16000  # Hz
BITS = 16            # bit mélység

# Mérési intervallum
SENSOR_INTERVAL = 2.0  # másodperc
MIC_INTERVAL = 0.2     # másodperc
```

---

**Fontos:** A Thonny automatikusan UTF-8 kódolással menti a fájlokat, így a magyar karakterek helyesen jelennek meg a Pico-n is!
