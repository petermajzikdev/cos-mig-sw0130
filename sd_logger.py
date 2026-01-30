from machine import SPI, Pin
import os

class SDLogger:
    """SD kártya adatmentés kezelő"""

    def __init__(self, sck_pin, mosi_pin, miso_pin, cs_pin):
        self.cs = Pin(cs_pin, Pin.OUT)
        self.cs.value(1)

        self.spi = SPI(0,
                       baudrate=1000000,
                       polarity=0,
                       phase=0,
                       sck=Pin(sck_pin),
                       mosi=Pin(mosi_pin),
                       miso=Pin(miso_pin))

        self.mounted = False
        self.buffer = []

    def mount(self):
        """SD kártya csatolása"""
        try:
            import sdcard
            sd = sdcard.SDCard(self.spi, self.cs)
            vfs = os.VfsFat(sd)
            os.mount(vfs, "/sd")
            self.mounted = True
            return True
        except:
            self.mounted = False
            return False

    def write_header(self, filename):
        """CSV fejléc írása"""
        if not self.mounted:
            return False

        try:
            with open(filename, 'w') as f:
                f.write("timestamp,temp_c,pressure_hpa,altitude_m,audio_rms\n")
            return True
        except:
            return False

    def append_data(self, filename, timestamp, temp, pressure, altitude, audio_rms):
        """Adat hozzáfűzése a CSV fájlhoz"""
        if not self.mounted:
            return False

        try:
            with open(filename, 'a') as f:
                f.write(f"{timestamp},{temp:.2f},{pressure:.2f},{altitude:.1f},{audio_rms:.4f}\n")
            return True
        except:
            return False

    def buffer_data(self, data):
        """Adat bufferelése (később kiíráshoz)"""
        self.buffer.append(data)

    def flush_buffer(self, filename):
        """Buffer kiírása fájlba"""
        if not self.mounted or not self.buffer:
            return False

        try:
            with open(filename, 'a') as f:
                for data in self.buffer:
                    f.write(data + "\n")
            self.buffer.clear()
            return True
        except:
            return False

    def unmount(self):
        """SD kártya leválasztása"""
        if self.mounted:
            try:
                os.umount("/sd")
                self.mounted = False
            except:
                pass
