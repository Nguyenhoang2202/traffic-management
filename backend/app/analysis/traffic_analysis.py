from app.websocket_routers.device_connecting import connecting_devices
from app.analysis.manager import send_command_to_device
import asyncio

def calculate_green_time(cover_ratio: float, num_current: int, predict_value: int,road_width: float, min_time: int = 15, max_time: int = 90) -> int:
    # 
    time_car = 10
    g_time1 = num_current*time_car/road_width
    g_time2 = cover_ratio*max_time

    predict_per_cycle = predict_value / 60  # Dự đoán số lượng xe trong 1 phút

    # Tính thời gian xanh cần cho lượng xe dự đoán
    g_time3 = predict_per_cycle * time_car / road_width
    # Tính thời gian đèn xanh dựa trên traffic_score
    green_time = int((0.2 * g_time1) + (0.6 * g_time2) + (0.2 * g_time3))
    # Giới hạn thời gian
    green_time = max(min_time, min(green_time, max_time))# Nếu thấp hơn min_time thì lấy min (max tương tự)
    return green_time

async def traffic_flow_analysis(device_id):
    green_time = 15
    green_time_longest = 0
    sent = False
    command_data = {}
    device = connecting_devices[device_id]
    all_green_time = 0  # Thời gian đèn xanh trung bình
    numb_turn_green = 0  # Số lần đèn xanh đã gửi lệnh
    while True:
        # Check reset_analyze
        if device["reset_analyze"]:
            all_green_time = 0
            numb_turn_green = 0
            device["reset_analyze"] = False
            print(f"Đã reset_analyze cho thiết bị {device_id}")

        await asyncio.sleep(1)  # tránh chiếm CPU 100%
        
        # Lấy thông tin dữ liệu từ rpi
        last_data = None
        while last_data == None:
            last_data = device["last_data"]
            await asyncio.sleep(0.5)
        # Lấy thông tin thiết bị
        mode = last_data["mode"]
        auto_mode = last_data["auto_mode"]
        state = last_data["traffic_light"]["state"]
        remaining_time = last_data["traffic_light"]["remaining_time"]
        # Lấy thông tin detect
        last_detect_data = None
        while last_detect_data == None:
            last_detect_data = device["last_detect_data"]
            await asyncio.sleep(0.5)
        # Lấy thông tin thiết bị
        num_current = last_detect_data["num_current"]
        cover_ratio = last_detect_data["cover_ratio"]
        # Lấy dự đoán gần nhất nếu có
        predict_value = device.get("last_predict_data")
        if predict_value is None:
            print(f"⚠️ Thiết bị {device_id} chưa có dữ liệu dự đoán, bỏ qua vòng lặp.")
            continue

        # Không phân tích 
        if mode == 1 or state != 0 or auto_mode == 0:
            continue

        # Trong thời gian đèn đỏ, nếu còn >= 3s → phân tích
        if remaining_time >= 3:
            print("analysis")
            green_time_temp = calculate_green_time(cover_ratio=cover_ratio,num_current=num_current,predict_value=predict_value,road_width=3.5,)
            if green_time_temp > green_time_longest:
                green_time_longest = green_time_temp
                green_time = green_time_longest
            continue

        # Khi đếm ngược còn < 3 giây và chưa gửi lệnh → gửi
        if not sent:
            # Cập nhập dữ liệu phân tích
            numb_turn_green += 1
            all_green_time += green_time
            last_analyze_data = device["last_analyze_data"]
            last_analyze_data["all_green_time"] = all_green_time
            last_analyze_data["numb_turn_green"] = numb_turn_green
            last_analyze_data["average_green_time"] = all_green_time / numb_turn_green if numb_turn_green > 0 else 0

            command_data["green_time"] = green_time
            try:
                # Gửi lệnh đến thiết bị
                await send_command_to_device(device_id=device_id, command_data=command_data)
                print("Sent command!")
                sent = True
            except Exception as e:
                print(f"❌ Thiết bị {device_id}: Gửi thất bại: {e}")
        # Khi xong 1 chu kỳ đèn đỏ → reset sent
        if remaining_time == 0:
            sent = False

# ---------------------------------------------------------------------------------------------------------------
# async def traffic_flow_analysis(device_id):
#     green_time = 0
#     sent = False
#     command_data = {}
#     device = connecting_devices[device_id]
#     all_green_time = 0  # Thời gian đèn xanh trung bình
#     numb_turn_green = 0  # Số lần đèn xanh đã gửi lệnh
#     while True:
#         # Check reset_analyze
#         if device["reset_analyze"]:
#             all_green_time = 0
#             numb_turn_green = 0
#             device["reset_analyze"] = False
#             print(f"Đã reset_analyze cho thiết bị {device_id}")

#         await asyncio.sleep(1)  # tránh chiếm CPU 100%
        
#         # Lấy thông tin dữ liệu từ rpi
#         last_data = None # Reset last_data
#         while last_data == None:
#             last_data = device["last_data"] # Lấy last_data từ thiết bị
#             await asyncio.sleep(0.5)
#         # Lấy thông tin thiết bị
#         mode = last_data["mode"]
#         auto_mode = last_data["auto_mode"]
#         state = last_data["traffic_light"]["state"]
#         remaining_time = last_data["traffic_light"]["remaining_time"]

#         # Lấy thông tin detect
#         last_detect_data = None
#         while last_detect_data == None:
#             last_detect_data = device["last_detect_data"]
#             await asyncio.sleep(0.5)
#         # Lấy thông tin thiết bị
#         num_current = last_detect_data["num_current"]
#         cover_ratio = last_detect_data["cover_ratio"]

#         # Lấy dự đoán gần nhất nếu có
#         predict_value = device.get("last_predict_data")
#         if predict_value is None:
#             print(f"⚠️ Thiết bị {device_id} chưa có dữ liệu dự đoán, bỏ qua vòng lặp.")
#             continue

#         # Không phân tích 
#         if mode == 1 or state != 0 or auto_mode == 0:
#             continue

#         # Trong thời gian đèn đỏ, nếu còn >= 3s → phân tích
#         if remaining_time >= 3:
#             print("analysis")
#             green_time = calculate_green_time(cover_ratio=cover_ratio,num_current=num_current,predict_value=predict_value,road_width=3.5,)
#             continue

#         # Khi đếm ngược còn < 3 giây và chưa gửi lệnh → gửi
#         if not sent:
#             # Cập nhập dữ liệu phân tích
#             numb_turn_green += 1
#             all_green_time += green_time
#             last_analyze_data = device["last_analyze_data"]
#             last_analyze_data["all_green_time"] = all_green_time
#             last_analyze_data["numb_turn_green"] = numb_turn_green
#             last_analyze_data["average_green_time"] = all_green_time / numb_turn_green if numb_turn_green > 0 else 0

#             command_data["green_time"] = green_time
#             try:
#                 # Gửi lệnh đến thiết bị
#                 await send_command_to_device(device_id=device_id, command_data=command_data)
#                 print("Sent command!")
#                 sent = True
#             except Exception as e:
#                 print(f"❌ Thiết bị {device_id}: Gửi thất bại: {e}")
#         # Khi xong 1 chu kỳ đèn đỏ → reset sent
#         if remaining_time == 0:
#             sent = False
# ---------------------------------------------------------------------------------------------------------------

# Tạo dictionary để lưu trữ các task phân tích cho từng thiết bị
analysing_tasks = dict()  # device_id -> asyncio.Task

async def run_all_analysis_tasks_forever():
    while True:
        # Tạo task mới nếu thiết bị mới kết nối
        for device_id in connecting_devices:
            if device_id not in analysing_tasks:
                task = asyncio.create_task(traffic_flow_analysis(device_id))
                analysing_tasks[device_id] = task
                print(f"✅ Đã tạo task PHÂN TÍCH cho: {device_id}")

        # Hủy task nếu thiết bị đã mất kết nối
        disconnected_ids = [did for did in analysing_tasks if did not in connecting_devices]
        for did in disconnected_ids:
            task = analysing_tasks.pop(did)
            if not task.done():
                task.cancel()
                print(f"⚠️ Đã hủy task phân tích cho thiết bị {did} do mất kết nối")

        await asyncio.sleep(2)