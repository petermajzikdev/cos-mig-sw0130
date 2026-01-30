from machine import Pin, Timer

class LEDController:
    """LED státusz és hibajelző kezelő"""

    def __init__(self, status_pin, error_pin):
        self.status_led = Pin(status_pin, Pin.OUT)
        self.error_led = Pin(error_pin, Pin.OUT)
        self.blink_timer = None
        self.status_led.value(0)
        self.error_led.value(0)

    def status_on(self):
        """Státusz LED bekapcsolás (normál működés)"""
        self.status_led.value(1)

    def status_off(self):
        """Státusz LED kikapcsolás"""
        self.status_led.value(0)

    def status_toggle(self):
        """Státusz LED átváltás"""
        self.status_led.value(not self.status_led.value())

    def error_on(self):
        """Hiba LED bekapcsolás"""
        self.error_led.value(1)

    def error_off(self):
        """Hiba LED kikapcsolás"""
        self.error_led.value(0)

    def error_blink(self, count=5, interval_ms=200):
        """
        Hiba LED villogtatás

        Args:
            count: Villogások száma
            interval_ms: Villogási intervallum milliszekundumban
        """
        for _ in range(count):
            self.error_led.value(1)
            Timer(-1).init(period=interval_ms, mode=Timer.ONE_SHOT, callback=lambda t: None)
            self.error_led.value(0)
            Timer(-1).init(period=interval_ms, mode=Timer.ONE_SHOT, callback=lambda t: None)

    def heartbeat(self):
        """Gyors státusz villanás (életjel)"""
        self.status_led.value(1)
        Timer(-1).init(period=50, mode=Timer.ONE_SHOT, callback=lambda t: self.status_led.value(0))
