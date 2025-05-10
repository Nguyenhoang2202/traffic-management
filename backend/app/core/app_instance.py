from fastapi import FastAPI
from app.websocket_routers.ws_fe import ws_fe_router
from app.websocket_routers.ws_device import ws_device_router
from app.api.routers import camera,traffic_data,user,command
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.include_router(ws_fe_router)
app.include_router(ws_device_router)
app.include_router(camera.router)
app.include_router(traffic_data.router)
app.include_router(user.router)
app.include_router(command.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # hoặc ["*"] để test
    allow_credentials=True,
    allow_methods=["*"],  # cần để chấp nhận cả OPTIONS
    allow_headers=["*"],
)