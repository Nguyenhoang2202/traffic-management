import asyncio
from gpiozero import DigitalInputDevice

class RainSensor:
    def __init__(self, pin=18, poll_interval=1.0):
        self.sensor = DigitalInputDevice(pin)
        self.poll_interval = poll_interval
        self.is_raining = False

    async def monitor(self):
        while True:
            self.is_raining = not self.sensor.is_active
            await asyncio.sleep(self.poll_interval)

    def get_status(self):
        """Trả về True nếu đang mưa, False nếu trời khô."""
        return self.is_raining
