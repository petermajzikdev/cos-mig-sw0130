"""
CanSat Ground Station (Vevőállomás)
LoRa telemetria fogadása és megjelenítése
"""

from machine import SPI, Pin
import time
from lora_radio import LoRaRadio
import config

class GroundStation:
    """Földi állomás telemetria fogadáshoz"""

    def __init__(self):
        # LoRa inicializálása fogadó módban
        self.lora = LoRaRadio(
            sck_pin=config.LORA_SCK,
            mosi_pin=config.LORA_MOSI,
            miso_pin=config.LORA_MISO,
            cs_pin=config.LORA_CS,
            rst_pin=config.LORA_RST,
            dio0_pin=config.LORA_DIO0
        )

        self.initialized = self.lora.init(
            frequency=config.LORA_FREQUENCY,
            tx_power=config.LORA_TX_POWER,
            spreading_factor=config.LORA_SPREADING_FACTOR,
            bandwidth=config.LORA_BANDWIDTH,
            coding_rate=config.LORA_CODING_RATE
        )

        self.packet_count = 0
        self.last_packet_time = 0

    def receive(self):
        """
        LoRa csomag fogadása

        Returns:
            dict: Telemetria adatok vagy None
        """
        if not self.initialized:
            return None

        try:
            # RX continuous mód
            self.lora._set_mode(self.lora.MODE_RX_CONTINUOUS)

            # IRQ flag ellenőrzése
            irq_flags = self.lora._read_register(self.lora.REG_IRQ_FLAGS)

            if irq_flags & 0x40:  # RxDone
                # Packet fogadva
                packet_length = self.lora._read_register(self.lora.REG_RX_NB_BYTES)
                fifo_addr = self.lora._read_register(self.lora.REG_FIFO)

                self.lora._write_register(self.lora.REG_FIFO_ADDR_PTR, fifo_addr)

                # FIFO olvasás
                self.lora.cs.value(0)
                self.lora.spi.write(bytes([self.lora.REG_FIFO & 0x7F]))
                data = self.lora.spi.read(packet_length)
                self.lora.cs.value(1)

                # IRQ flag törlése
                self.lora._write_register(self.lora.REG_IRQ_FLAGS, 0xFF)

                # Adat dekódolása
                message = data.decode('utf-8', 'ignore')
                return self.parse_telemetry(message)

            return None

        except:
            return None

    def parse_telemetry(self, message):
        """
        Telemetria üzenet feldolgozása

        Formátum: "ID,seq,temp,pres,alt,audio"

        Returns:
            dict: Telemetria adatok
        """
        try:
            parts = message.split(',')
            if len(parts) >= 6:
                self.packet_count += 1
                self.last_packet_time = time.time()

                return {
                    'mission_id': parts[0],
                    'sequence': int(parts[1]),
                    'temperature': float(parts[2]),
                    'pressure': float(parts[3]),
                    'altitude': float(parts[4]),
                    'audio_rms': float(parts[5]),
                    'rssi': self.get_rssi(),
                    'timestamp': time.time()
                }
        except:
            pass

        return None

    def get_rssi(self):
        """
        RSSI (Received Signal Strength Indicator) lekérése

        Returns:
            int: RSSI érték dBm-ben
        """
        rssi_value = self.lora._read_register(0x1A)
        return -157 + rssi_value

    def display_telemetry(self, data):
        """Telemetria megjelenítése"""
        if data:
            print("=" * 60)
            print(f"Mission ID: {data['mission_id']}")
            print(f"Packet #: {data['sequence']}")
            print(f"Temperature: {data['temperature']:.2f} °C")
            print(f"Pressure: {data['pressure']:.2f} hPa")
            print(f"Altitude: {data['altitude']:.1f} m")
            print(f"Audio RMS: {data['audio_rms']:.4f}")
            print(f"RSSI: {data['rssi']} dBm")
            print(f"Time: {data['timestamp']:.2f}")
            print("=" * 60)

    def log_to_file(self, data, filename="ground_station_log.csv"):
        """Telemetria mentése fájlba"""
        try:
            with open(filename, 'a') as f:
                f.write(f"{data['timestamp']},{data['mission_id']},{data['sequence']},"
                       f"{data['temperature']},{data['pressure']},{data['altitude']},"
                       f"{data['audio_rms']},{data['rssi']}\n")
        except:
            pass


def main():
    """Vevőállomás főprogram"""
    print("CanSat Ground Station")
    print("=" * 60)

    station = GroundStation()

    if not station.initialized:
        print("ERROR: LoRa initialization failed!")
        return

    print("Waiting for telemetry...")
    print("Press Ctrl+C to stop")
    print()

    try:
        while True:
            data = station.receive()

            if data:
                station.display_telemetry(data)
                station.log_to_file(data)

            time.sleep_ms(100)

    except KeyboardInterrupt:
        print("\nGround station stopped.")
        print(f"Total packets received: {station.packet_count}")


if __name__ == "__main__":
    main()
