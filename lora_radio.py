from machine import SPI, Pin
import time

class LoRaRadio:
    """
    LoRa rádió kommunikáció (RFM95W / SX1276 / SX1278)
    Egyszerűsített telemetria küldéshez
    """

    # SX127x regiszter címek
    REG_FIFO = 0x00
    REG_OP_MODE = 0x01
    REG_FRF_MSB = 0x06
    REG_FRF_MID = 0x07
    REG_FRF_LSB = 0x08
    REG_PA_CONFIG = 0x09
    REG_LNA = 0x0C
    REG_FIFO_ADDR_PTR = 0x0D
    REG_FIFO_TX_BASE_ADDR = 0x0E
    REG_FIFO_RX_BASE_ADDR = 0x0F
    REG_IRQ_FLAGS = 0x12
    REG_RX_NB_BYTES = 0x13
    REG_MODEM_CONFIG_1 = 0x1D
    REG_MODEM_CONFIG_2 = 0x1E
    REG_PREAMBLE_MSB = 0x20
    REG_PREAMBLE_LSB = 0x21
    REG_PAYLOAD_LENGTH = 0x22
    REG_MODEM_CONFIG_3 = 0x26
    REG_DIO_MAPPING_1 = 0x40
    REG_VERSION = 0x42
    REG_PA_DAC = 0x4D

    # Módok
    MODE_SLEEP = 0x00
    MODE_STDBY = 0x01
    MODE_TX = 0x03
    MODE_RX_CONTINUOUS = 0x05
    MODE_LORA = 0x80

    def __init__(self, sck_pin, mosi_pin, miso_pin, cs_pin, rst_pin, dio0_pin=None):
        self.cs = Pin(cs_pin, Pin.OUT)
        self.rst = Pin(rst_pin, Pin.OUT)
        self.cs.value(1)
        self.rst.value(1)

        self.spi = SPI(1,
                       baudrate=5000000,
                       polarity=0,
                       phase=0,
                       sck=Pin(sck_pin),
                       mosi=Pin(mosi_pin),
                       miso=Pin(miso_pin))

        self.initialized = False

    def reset(self):
        """LoRa modul reset"""
        self.rst.value(0)
        time.sleep_ms(10)
        self.rst.value(1)
        time.sleep_ms(10)

    def _write_register(self, address, value):
        """Regiszter írás"""
        self.cs.value(0)
        self.spi.write(bytes([address | 0x80, value]))
        self.cs.value(1)

    def _read_register(self, address):
        """Regiszter olvasás"""
        self.cs.value(0)
        self.spi.write(bytes([address & 0x7F]))
        data = self.spi.read(1)
        self.cs.value(1)
        return data[0]

    def _set_mode(self, mode):
        """Működési mód beállítása"""
        self._write_register(self.REG_OP_MODE, self.MODE_LORA | mode)

    def init(self, frequency=868.0, tx_power=14, spreading_factor=7, bandwidth=125000, coding_rate=5):
        """
        LoRa inicializálása

        Args:
            frequency: Frekvencia MHz-ben (pl. 868.0, 915.0)
            tx_power: Adóteljesítmény dBm-ben (5-20)
            spreading_factor: 7-12
            bandwidth: 125000, 250000, 500000 Hz
            coding_rate: 5-8
        """
        self.reset()

        # Verzió ellenőrzés
        version = self._read_register(self.REG_VERSION)
        if version != 0x12:
            return False

        # Sleep mód
        self._set_mode(self.MODE_SLEEP)
        time.sleep_ms(10)

        # Frekvencia beállítása
        frf = int((frequency * 1000000.0) / 32000000.0 * 524288.0)
        self._write_register(self.REG_FRF_MSB, (frf >> 16) & 0xFF)
        self._write_register(self.REG_FRF_MID, (frf >> 8) & 0xFF)
        self._write_register(self.REG_FRF_LSB, frf & 0xFF)

        # Adóteljesítmény
        if tx_power > 17:
            tx_power = 17
        elif tx_power < 2:
            tx_power = 2
        self._write_register(self.REG_PA_CONFIG, 0x80 | (tx_power - 2))

        # LNA
        self._write_register(self.REG_LNA, 0x23)

        # Bandwidth és Coding Rate
        bw_map = {125000: 7, 250000: 8, 500000: 9}
        bw_value = bw_map.get(bandwidth, 7)
        self._write_register(self.REG_MODEM_CONFIG_1, (bw_value << 4) | ((coding_rate - 4) << 1))

        # Spreading Factor
        self._write_register(self.REG_MODEM_CONFIG_2, (spreading_factor << 4) | 0x04)

        # Preamble
        self._write_register(self.REG_PREAMBLE_MSB, 0x00)
        self._write_register(self.REG_PREAMBLE_LSB, 0x08)

        # FIFO
        self._write_register(self.REG_FIFO_TX_BASE_ADDR, 0x00)
        self._write_register(self.REG_FIFO_RX_BASE_ADDR, 0x00)

        # Standby mód
        self._set_mode(self.MODE_STDBY)

        self.initialized = True
        return True

    def send(self, data):
        """
        Adat küldése

        Args:
            data: bytes vagy string
        """
        if not self.initialized:
            return False

        if isinstance(data, str):
            data = data.encode()

        # Standby mód
        self._set_mode(self.MODE_STDBY)

        # FIFO reset
        self._write_register(self.REG_FIFO_ADDR_PTR, 0x00)

        # Adat írása FIFO-ba
        self.cs.value(0)
        self.spi.write(bytes([self.REG_FIFO | 0x80]))
        self.spi.write(data)
        self.cs.value(1)

        # Csomag hossz
        self._write_register(self.REG_PAYLOAD_LENGTH, len(data))

        # TX mód
        self._set_mode(self.MODE_TX)

        # Várakozás átvitelre (IRQ flag)
        timeout = 100
        while timeout > 0:
            irq_flags = self._read_register(self.REG_IRQ_FLAGS)
            if irq_flags & 0x08:  # TxDone
                break
            time.sleep_ms(10)
            timeout -= 1

        # IRQ flag törlése
        self._write_register(self.REG_IRQ_FLAGS, 0xFF)

        # Standby mód
        self._set_mode(self.MODE_STDBY)

        return timeout > 0

    def send_telemetry(self, packet_id, temp, pressure, altitude, audio_rms):
        """
        Telemetria csomag küldése kompakt formátumban

        Formátum: "ID,seq,temp,pres,alt,audio"
        Példa: "CANSAT01,123,25.34,1013.25,150.2,0.1234"
        """
        message = f"{packet_id[0]},{packet_id[1]},{temp:.2f},{pressure:.2f},{altitude:.1f},{audio_rms:.4f}"
        return self.send(message)
