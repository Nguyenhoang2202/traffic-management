import RPi.GPIO as GPIO
import asyncio
import time
PIN_MAP = {
    'A': 26,
    'B': 19,
    'C': 21,
    'D': 24,
    'E': 16,
    'F': 5,
    'G': 23,
    'DP': 20,
    'DIGIT1': 6,
    'DIGIT2': 13
}

SEGMENT_ENCODING = {
    '0': ['A', 'B', 'C', 'D', 'E', 'F'],
    '1': ['B', 'C'],
    '2': ['A', 'B', 'G', 'E', 'D'],
    '3': ['A', 'B', 'C', 'D', 'G'],
    '4': ['F', 'G', 'B', 'C'],
    '5': ['A', 'F', 'G', 'C', 'D'],
    '6': ['A', 'F', 'E', 'D', 'C', 'G'],
    '7': ['A', 'B', 'C'],
    '8': ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
    '9': ['A', 'B', 'C', 'D', 'F', 'G']
}

class SevenSegmentDisplay:
    def __init__(self):
        self.current_number = "00"
        self.lock = asyncio.Lock()
        self.running = True
        for pin in PIN_MAP.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)  # Tắt toàn bộ

    async def update_number(self, number: int):
        number = str(number).zfill(2)
        async with self.lock:
            self.current_number = number

    def clear_segments(self):
        for segment in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'DP']:
            GPIO.output(PIN_MAP[segment], GPIO.HIGH)

    def display_digit(self, digit):
        self.clear_segments()
        for segment in SEGMENT_ENCODING.get(str(digit), []):
            GPIO.output(PIN_MAP[segment], GPIO.LOW)

    async def run(self):
        while self.running:
            async with self.lock:
                left_digit, right_digit = self.current_number[0], self.current_number[1]

            # Hiển thị digit bên trái
            GPIO.output(PIN_MAP['DIGIT2'], GPIO.HIGH)
            self.display_digit(left_digit)
            GPIO.output(PIN_MAP['DIGIT1'], GPIO.LOW)
            await asyncio.sleep(0.003)

            # Hiển thị digit bên phải
            GPIO.output(PIN_MAP['DIGIT1'], GPIO.HIGH)
            self.display_digit(right_digit)
            GPIO.output(PIN_MAP['DIGIT2'], GPIO.LOW)
            await asyncio.sleep(0.003)

        # Tắt khi kết thúc
        GPIO.output(PIN_MAP['DIGIT1'], GPIO.HIGH)
        GPIO.output(PIN_MAP['DIGIT2'], GPIO.HIGH)
        self.clear_segments()
        
    async def show(self, number, duration=1):
        number = str(number).zfill(2)
        left_digit, right_digit = number[0], number[1]

        end_time = asyncio.get_event_loop().time() + duration
        while asyncio.get_event_loop().time() < end_time:
            # Trái
            GPIO.output(PIN_MAP['DIGIT2'], GPIO.HIGH)
            self.display_digit(left_digit)
            GPIO.output(PIN_MAP['DIGIT1'], GPIO.LOW)
            await asyncio.sleep(0.005)

            # Phải
            GPIO.output(PIN_MAP['DIGIT1'], GPIO.HIGH)
            self.display_digit(right_digit)
            GPIO.output(PIN_MAP['DIGIT2'], GPIO.LOW)
            await asyncio.sleep(0.005)

        GPIO.output(PIN_MAP['DIGIT1'], GPIO.HIGH)
        GPIO.output(PIN_MAP['DIGIT2'], GPIO.HIGH)
        self.clear_segments()

        
    def show_blocking(self, number, duration=1):
        number = str(number).zfill(2)
        left_digit, right_digit = number[0], number[1]

        end_time = time.time() + duration
        while time.time() < end_time:
            # Trái
            GPIO.output(PIN_MAP['DIGIT2'], GPIO.HIGH)
            self.display_digit(left_digit)
            GPIO.output(PIN_MAP['DIGIT1'], GPIO.LOW)
            time.sleep(0.01)

            # Phải
            GPIO.output(PIN_MAP['DIGIT1'], GPIO.HIGH)
            self.display_digit(right_digit)
            GPIO.output(PIN_MAP['DIGIT2'], GPIO.LOW)
            time.sleep(0.01)

        GPIO.output(PIN_MAP['DIGIT1'], GPIO.HIGH)
        GPIO.output(PIN_MAP['DIGIT2'], GPIO.HIGH)
        self.clear_segments()


# Ví dụ sử dụng trong main.py:
# 
# from countdown_light import SevenSegmentDisplay
# 
# display = SevenSegmentDisplay()
# await display.show(45, duration=1)
# display.cleanup()