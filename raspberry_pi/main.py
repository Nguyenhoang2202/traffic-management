import RPi.GPIO as GPIO
import time
from devices.traffic_light import traffic_light
from devices.countdown_light import SevenSegmentDisplay
from sensors.rain import RainSensor
from sensors.gps import GPSReader 
from camera import Camera
from connect_server import connect_forever
import asyncio

"""
DEVICE_ID
"""
device_id = "C1"


red_time = 14
green_time = 15

GPIO.setmode(GPIO.BCM)

async def update_display_loop(traffic_light, display):
    while True:
        mode = traffic_light.mode
        if mode == 1:
            await asyncio.sleep(0.5)
            continue
        remaining_time = traffic_light.get_remaining_time()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, display.show_blocking, remaining_time, 0.2)


def safe_task(coro, name):
    async def wrapper():
        try:
            await coro
        except asyncio.CancelledError:
            print(f"🛑 Task '{name}' bị hủy.")
        except Exception as e:
            print(f"❌ Lỗi trong task '{name}': {e}")
            traceback.print_exc()
    return asyncio.create_task(wrapper(), name=name)

# Hàm main
async def main():
    # Khởi tạo thiết bị
    gps = GPSReader()
    trafficLight = traffic_light(green_time, red_time)
    SevenSegment_display = SevenSegmentDisplay()
    rainStatus = RainSensor()
    camera = Camera()

    # Tạo task an toàn
    displayTL     = safe_task(trafficLight.run(), "TrafficLight")
    displayCDL    = safe_task(update_display_loop(trafficLight, SevenSegment_display), "CountdownDisplay")
    getRainStatus = safe_task(rainStatus.monitor(), "RainSensor")
    getFrame      = safe_task(camera.run(), "Camera")
    send_data     = safe_task(connect_forever(device_id=device_id, camera=camera, rain_sensor=rainStatus, gps=gps, tlight=trafficLight), "Sender")

    # Duy trì vòng lặp vô hạn để hệ thống luôn chạy
    while True:
        await asyncio.sleep(5)  # Chờ để giữ event loop sống

# Run
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🧹 Đang dọn dẹp và thoát...")
        GPIO.cleanup()
