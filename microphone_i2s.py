from machine import I2S, Pin

class I2S_Microphone:
    """
    Adafruit I2S MEMS mikrofon kezelő osztály Raspberry Pi Pico-hoz
    - ICS-43434
    """

    def __init__(self, sck_pin=16, ws_pin=17, sd_pin=18, sample_rate=16000, bits=16):
        """
        I2S mikrofon inicializálása

        Args:
            sck_pin: Bit Clock (BCLK/SCK) pin száma
            ws_pin: Word Select (WS/LRCLK) pin száma
            sd_pin: Serial Data (SD/DOUT) pin száma
            sample_rate: Mintavételi frekvencia Hz-ben (alapértelmezett: 16000)
            bits: Bit mélység (16 vagy 32)
        """
        self.sample_rate = sample_rate
        self.bits = bits
        self.initialized = False

        try:
            # I2S periféria konfigurálása
            self.audio_in = I2S(
                0,  # I2S ID (0 vagy 1 a Pico-n)
                sck=Pin(sck_pin),
                ws=Pin(ws_pin),
                sd=Pin(sd_pin),
                mode=I2S.RX,  # Receive mode (mikrofonról olvasás)
                bits=bits,
                format=I2S.MONO,  # Mono audio
                rate=sample_rate,
                ibuf=2048  # Internal buffer size
            )
            self.initialized = True
        except:
            self.initialized = False

    def read_samples(self, num_samples=1024):
        """
        Audio minták olvasása a mikrofonból

        Args:
            num_samples: Olvasandó minták száma

        Returns:
            bytearray: Nyers audio adat
        """
        # Buffer mérete = num_samples * (bits / 8)
        bytes_per_sample = self.bits // 8
        audio_buffer = bytearray(num_samples * bytes_per_sample)

        num_bytes_read = self.audio_in.readinto(audio_buffer)

        return audio_buffer[:num_bytes_read]

    def read_samples_as_integers(self, num_samples=1024):
        """
        Audio minták olvasása egész számokként

        Args:
            num_samples: Olvasandó minták száma

        Returns:
            list: Egész számok listája
        """
        audio_buffer = self.read_samples(num_samples)

        if self.bits == 16:
            # 16-bit signed integer konverzió
            samples = []
            for i in range(0, len(audio_buffer), 2):
                if i + 1 < len(audio_buffer):
                    # Little-endian 16-bit signed
                    sample = int.from_bytes(audio_buffer[i:i+2], 'little', True)
                    samples.append(sample)
            return samples
        elif self.bits == 32:
            # 32-bit signed integer konverzió
            samples = []
            for i in range(0, len(audio_buffer), 4):
                if i + 3 < len(audio_buffer):
                    # Little-endian 32-bit signed
                    sample = int.from_bytes(audio_buffer[i:i+4], 'little', True)
                    samples.append(sample)
            return samples

        return []

    def get_rms_level(self, num_samples=512):
        """
        RMS (Root Mean Square) hangerő szint számítása

        Args:
            num_samples: Minták száma a számításhoz

        Returns:
            float: RMS érték (0-1 között normalizálva)
        """
        if not self.initialized:
            return 0.0

        samples = self.read_samples_as_integers(num_samples)

        if not samples:
            return 0.0

        # RMS számítás
        sum_squares = sum(s * s for s in samples)
        mean_square = sum_squares / len(samples)
        rms = (mean_square ** 0.5)

        # Normalizálás a bit mélység alapján
        max_value = 2 ** (self.bits - 1)
        normalized_rms = rms / max_value

        return normalized_rms

    def deinit(self):
        """I2S periféria leállítása"""
        if self.initialized:
            self.audio_in.deinit()
            self.initialized = False
