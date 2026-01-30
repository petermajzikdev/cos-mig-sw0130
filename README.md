# CanSat Telemetria Rendszer

Raspberry Pi Pico alapú CanSat telemetria rendszer hőmérséklet, légnyomás, magasság és audio méréshez.

## 📦 Komponensek

- **Raspberry Pi Pico** - Mikrokontroller
- **BMP280** - Hőmérséklet és légnyomás szenzor (I2C)
- **Adafruit I2S MEMS Mikrofon** (ICS-43434 vagy SPH0645LM4H)
- **LoRa modul** (RFM95W / SX1276 / SX1278)
- **MicroSD kártya modul** (SPI)
- **LED indikátorok** (Zöld státusz, Piros hiba)

## 🔌 Bekötési Táblázat

### BMP280 (I2C)
| BMP280 | Pico GPIO |
|--------|-----------|
| VCC    | 3.3V      |
| GND    | GND       |
| SCL    | GPIO 1    |
| SDA    | GPIO 0    |

### I2S MEMS Mikrofon
| Mikrofon | Pico GPIO |
|----------|-----------|
| VCC/3V   | 3.3V      |
| GND      | GND       |
| BCLK/SCK | GPIO 16   |
| LRCLK/WS | GPIO 17   |
| DOUT/SD  | GPIO 18   |
| SEL      | GND (bal csatorna) |

### LoRa Modul (SPI)
| LoRa   | Pico GPIO |
|--------|-----------|
| VCC    | 3.3V      |
| GND    | GND       |
| SCK    | GPIO 10   |
| MOSI   | GPIO 11   |
| MISO   | GPIO 12   |
| CS/NSS | GPIO 13   |
| RST    | GPIO 14   |
| DIO0   | GPIO 15   |

### SD Kártya (SPI)
| SD Modul | Pico GPIO |
|----------|-----------|
| VCC      | 3.3V      |
| GND      | GND       |
| SCK      | GPIO 2    |
| MOSI     | GPIO 3    |
| MISO     | GPIO 4    |
| CS       | GPIO 5    |

### LED Indikátorok
| LED         | Pico GPIO | Funkció |
|-------------|-----------|---------|
| Zöld LED    | GPIO 20   | Státusz / Életjel |
| Piros LED   | GPIO 21   | Hiba jelzés |

## 📂 Fájlstruktúra

```
├── config.py              # Konfiguráció (pinout, frekvenciák)
├── bmp280.py              # BMP280 driver
├── microphone_i2s.py      # I2S mikrofon driver
├── lora_radio.py          # LoRa kommunikáció
├── sd_logger.py           # SD kártya naplózás
├── led_controller.py      # LED vezérlés
├── cansat_main.py         # Főprogram (CanSat-re feltöltendő)
└── ground_station.py      # Vevőállomás kód
```

## 🚀 Használat

### 1. CanSat Program Feltöltése

```bash
# Másold a Pico-ra az összes fájlt
# A cansat_main.py-t nevezd át main.py-ra automatikus indításhoz
```

### 2. Konfiguráció

Módosítsd a `config.py` fájlban:
- GPIO pineket (ha eltérő bekötést használsz)
- LoRa frekvenciát (868 MHz EU / 915 MHz USA)
- Mintavételi paramétereket
- Mission ID-t

### 3. Működés

A CanSat automatikusan elindul bekapcsoláskor:
- **Zöld LED világít**: Rendszer működik
- **Zöld LED villan**: LoRa csomag elküldve
- **Piros LED villog**: Hiba történt
  - 1 villogás: Szenzor/küldési hiba
  - 2 villogás: SD kártya hiba
  - 3 villogás: Inicializálási hiba
  - 5 villogás: Kritikus hiba

### 4. Telemetria Formátum

LoRa csomag formátuma:
```
MISSION_ID,PACKET_NUM,TEMP,PRESSURE,ALTITUDE,AUDIO_RMS
```

Példa:
```
CANSAT01,123,25.34,1013.25,150.2,0.1234
```

### 5. SD Kártya Log

CSV formátum (`cansat_log.csv`):
```csv
timestamp,temp_c,pressure_hpa,altitude_m,audio_rms
0.50,25.34,1013.25,150.2,0.1234
1.50,25.32,1012.80,155.8,0.1456
```

## 📡 Vevőállomás

Másik Pico-n futtasd a `ground_station.py`-t:

```python
python ground_station.py
```

Ez fogadja és megjeleníti a telemetria csomagokat.

## ⚙️ Telemetria Intervallum

Alapértelmezett: **1 másodperc**

Módosítás a `config.py`-ban:
```python
TELEMETRY_INTERVAL = 1.0  # másodperc
```

## 🔧 Hibaelhárítás

### BMP280 nem észlelhető
- Ellenőrizd az I2C bekötést (SCL/SDA)
- Ellenőrizd a címet (0x76 vagy 0x77)

### I2S mikrofon nem működik
- Ellenőrizd a 3.3V tápellátást
- SEL pin bekötése fontos (GND = bal csatorna)

### LoRa nem küld
- Ellenőrizd az antenna csatlakozását
- Frekvencia egyezik a vevővel?
- SPI bekötés helyes?

### SD kártya nem működik
- Formázd FAT32-re
- Ellenőrizd az SPI bekötést
- CS pin helyesen van bekötve?

## 📊 Adatgyűjtés Specifikációk

- **BMP280**: 0.5-2 sec frissítés
- **I2S Mikrofon**: 8 kHz mintavétel, 128 minta RMS számításhoz
- **LoRa hatótáv**: ~2-5 km (tereptől függően)
- **SD kártya**: Automatikus mentés minden mérés után

## 📝 Verzió

v1.0 - Kezdeti kiadás CanSat versenyhez
