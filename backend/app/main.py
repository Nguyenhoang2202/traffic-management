import uvicorn
import asyncio
from app.core.app_instance import app
from app.analysis.traffic_analysis import run_all_analysis_tasks_forever
from app.detect.detect_data import run_all_detect_tasks_forever
from app.database.database import auto_send_data


async def run_server():
    """Chạy WebSocket server (FastAPI)"""
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8222, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":

    async def main():
        try:
            # Khởi tạo các task nền
            asyncio.create_task(run_server())
            asyncio.create_task(run_all_analysis_tasks_forever())
            asyncio.create_task(run_all_detect_tasks_forever())
            asyncio.create_task(auto_send_data())  # Thay đổi thời gian gửi dữ liệu nếu cần thiết
            # Giữ event loop sống
            while True:
                await asyncio.sleep(5)

        except asyncio.CancelledError:
            print("Tasks cancelled, shutting down gracefully...")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("❗ Đã dừng chương trình bằng Ctrl+C")
