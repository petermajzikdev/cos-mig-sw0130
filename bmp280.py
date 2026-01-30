from machine import I2C
import time
import struct

class BMP280:
    def __init__(self, i2c, addr=0x76):
        self.i2c = i2c
        self.addr = addr
        self._load_calibration()
        self.i2c.writeto_mem(self.addr, 0xF4, b'\x27')
        self.i2c.writeto_mem(self.addr, 0xF5, b'\xA0')

    def _load_calibration(self):
        calib = self.i2c.readfrom_mem(self.addr, 0x88, 24)
        self.cal = struct.unpack('<HhhHhhhhhhhh', calib)

    def read(self):
        data = self.i2c.readfrom_mem(self.addr, 0xF7, 6)
        adc_p = (data[0]<<12) | (data[1]<<4) | (data[2]>>4)
        adc_t = (data[3]<<12) | (data[4]<<4) | (data[5]>>4)

        t_fine = self._compensate_temp(adc_t)
        pressure = self._compensate_pressure(adc_p, t_fine)

        return pressure / 100, self.temperature / 100

    def _compensate_temp(self, adc_t):
        c = self.cal
        var1 = (((adc_t>>3) - (c[0]<<1)) * c[1]) >> 11
        var2 = (((((adc_t>>4) - c[0]) * ((adc_t>>4) - c[0])) >> 12) * c[2]) >> 14
        t_fine = var1 + var2
        self.temperature = (t_fine * 5 + 128) >> 8
        return t_fine

    def _compensate_pressure(self, adc_p, t_fine):
        c = self.cal
        var1 = t_fine - 128000
        var2 = var1 * var1 * c[5]
        var2 = var2 + ((var1 * c[4]) << 17)
        var2 = var2 + (c[3] << 35)
        var1 = ((var1 * var1 * c[2]) >> 8) + ((var1 * c[1]) << 12)
        var1 = (((1 << 47) + var1) * c[0]) >> 33
        if var1 == 0:
            return 0
        p = 1048576 - adc_p
        p = (((p << 31) - var2) * 3125) // var1
        var1 = (c[8] * (p >> 13) * (p >> 13)) >> 25
        var2 = (c[7] * p) >> 19
        return ((p + var1 + var2) >> 8) + (c[6] << 4)
