from fastapi import FastAPI
from app.websocket_routers.ws_fe import ws_fe_router
from app.websocket_routers.ws_device import ws_device_router
from app.api.routers import camera,traffic_data,user,command,predict
from fastapi.middleware.cors import CORSMiddleware

from app.predict.load_model import load_model_and_scaler

app = FastAPI()

load_model_and_scaler()

app.include_router(ws_fe_router)
app.include_router(ws_device_router)
app.include_router(camera.router)
app.include_router(traffic_data.router)
app.include_router(user.router)
app.include_router(command.router)
app.include_router(predict.router)

app.add_middleware(
    CORSMiddleware,
    # "http://localhost:3000",
        # "http://192.168.43.247:3000"
    allow_origins=["*"],  # hoặc ["*"] để test
    allow_credentials=True,
    allow_methods=["*"],  # cần để chấp nhận cả OPTIONS
    allow_headers=["*"],
)
