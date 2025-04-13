import RPi.GPIO as GPIO
import time
import asyncio


class led():
    def __init__(self,pin,color,time_on):
        self.pin = pin
        self.color = color
        self.time_on = time_on
        self.remaining_time = 0
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW) 

    async def turn_on(self):
        GPIO.output(self.pin, GPIO.HIGH)
        await self.countdown()
        GPIO.output(self.pin, GPIO.LOW)

    async def rain_turn_on(self):
        GPIO.output(self.pin, GPIO.HIGH)
        await asyncio.sleep(self.time_on)
        GPIO.output(self.pin, GPIO.LOW)
        await asyncio.sleep(self.time_on)

    async def countdown(self):
        for i in range(self.time_on, -1, -1):
            self.remaining_time = i 
            await asyncio.sleep(1)

class traffic_light_state():
    def __init__(self):
        self.state = 0
        self.pre_state = 2

    def change_state(self):
        self.state = (self.state+1)%3
    def is_change(self):
        if(self.state!=self.pre_state):
            self.pre_state=self.state
            return True
        return False

RED_PIN = 17
YELLOW_PIN = 27
GREEN_PIN = 22

class traffic_light():
    def __init__(self,go_time,stop_time):
        self.r = led(RED_PIN,0,time_on=stop_time)
        self.g = led(GREEN_PIN,1,time_on=go_time)
        self.y = led(YELLOW_PIN,2,time_on=3)
        self.y_rain = led(YELLOW_PIN,2,time_on=0.5)
        self.state = traffic_light_state()
        self.mode = 0
        self.auto_mode = 1 

    def set_mode(self, mode:int):
        self.mode = mode

    def update_timings(self, go_time: int, stop_time: int):
        if go_time:
            self.g.time_on = go_time
        if stop_time:
            self.r.time_on = stop_time

    def get_remaining_time(self):
        """Lấy số giây còn lại của đèn đang bật."""
        if self.state.state == 0:
            return self.r.remaining_time
        elif self.state.state == 1:
            return self.g.remaining_time
        elif self.state.state == 2:
            return self.y.remaining_time
        return 0
        
    async def nomal_mode(self):
        if(self.state.is_change()):
            if self.state.state == 0:  # Đèn đỏ
                await self.r.turn_on()
            elif self.state.state == 1:  # Đèn xanh
                await self.g.turn_on()
            elif self.state.state == 2:  # Đèn vàng
                await self.y.turn_on()
            self.state.change_state()

    async def rain_mode(self):
        await self.y_rain.rain_turn_on()

    async def run(self):
        while True:
            if(self.mode==0):
                await self.nomal_mode()
            elif(self.mode==1):
                await self.rain_mode()
        


