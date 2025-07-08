'use client';
import { useEffect, useState } from "react";
import { WebSocketClient } from "@/lib/api/websocket/wsClient";
import style from "./index.module.scss"
import Form, { FieldType } from "@/components/common/Form";
import { createCommand } from "@/lib/api/manager/post_command";
// device_id: str                
// mode: Optional[int] = None
// auto_mode: Optional[bool] = None
// green_time: Optional[int] = None
// red_time: Optional[int] = None
const formPostCommand = [
    { name: 'device_id', type: 'text' as FieldType, label: 'Camera ID', },
    { name: 'mode', type: 'number' as FieldType, label: 'Chế độ đèn (0:Bình thường, 1:Nhấp nháy)', min: 0, max: 1, },
    { name: 'auto_mode', type: 'select' as FieldType, label: 'Tự động điều chỉnh', option: ['true', 'false'] },
    { name: 'green_time', type: 'number' as FieldType, label: 'Thời gian đèn xanh', min: 0, max: 200, },
    { name: 'red_time', type: 'number' as FieldType, label: 'Thời gian đèn đỏ', min: 0, max: 200, },
]
interface DeviceData {
    light_state: number;
    remaining_time: number;
    device_id: string;
    img_detected: string;
    num_current: number;
    num_total: number;
    cover_ratio: number;
    mode: number;
    auto_mode: number;

}
const TrafficMonitor = () => {
    // State dữ liệu post command
    const [postCommandData, setPostCommandData] = useState<Record<string, string>>(
        formPostCommand.reduce((acc, field) => (
            { ...acc, [field.name]: "" }
        ), {})
    );
    // State hiển thị form
    const [mode, setMode] = useState<"command" | null>(null)
    // Các camera
    const [devices, setDevices] = useState<DeviceData[]>([]);
    useEffect(() => {
        const wsClient = new WebSocketClient((data) => {
            setDevices(data);
        }, 1, 4);

        return () => {
            wsClient.closeManually(); // Chỉ đóng nếu thật sự muốn ngắt toàn bộ
        };
    }, []);

    // Hàm theo dõi thay đổi dữ liệu trong form
    const formPostChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setPostCommandData((prevData) => ({
            ...prevData, [name]: value,
        }));
    };
    // Post
    const handlePost = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        console.log(postCommandData);
        try {
            const newSetting = await createCommand(postCommandData);
            if (newSetting.detail) {
                alert(newSetting.detail);
            }
            else {
                alert("Thiết lập thành công!");
            }
        } catch (error) {
            console.error("Error creating service:", error);
        }
    };
    // Bật tắt form
    const changeMode = (
        e: React.MouseEvent<HTMLElement>,
        mode: "command" | null,
        deviceId?: string
    ) => {
        if (e.target !== e.currentTarget) return;
        if (deviceId) {
            setPostCommandData((prevData) => ({
                ...prevData,
                device_id: deviceId,
            }));
        }
        setMode(mode);
    };
    const pageSize = 4;
    return (
        <div className={style.container} >
            <h1 className={style.title_total}>DANH SÁCH CAMERA</h1>
            <div className={style.list_camera}>
                {
                    Array.from({ length: pageSize }).map((_, index) => {
                        const device = devices[index];
                        return (
                            <div key={index} className={style.camera}>
                                {device ? (
                                    <>
                                        <h4 className={style.title}>Camera: {device.device_id}</h4>

                                        <div className={style.videoWrapper}>
                                            <img
                                                src={`data:image/jpeg;base64,${device.img_detected}`}
                                                alt="Detected"
                                                className={style.video}
                                            />
                                        </div>

                                        <div className={style.info}>
                                            <p>
                                                {
                                                    device.light_state === 0 ? `🔴 - Time: ${device.remaining_time}s` :
                                                        device.light_state === 1 ? `🟢 - Time: ${device.remaining_time}s` :
                                                            device.light_state === 2 ? `🟡 - Time: ${device.remaining_time}s` :
                                                                device.light_state === 3 ? `🟡 - Nhấp nháy` :
                                                                    `⚫ Không xác định`
                                                }
                                            </p>
                                            <p>Số xe đang có: {device.num_current}</p>
                                            <p>Tổng xe: {device.num_total}</p>
                                            <p>Mức độ che phủ: {device.cover_ratio.toFixed(2)}</p>
                                            <p>
                                                {
                                                    device.mode === 0 ? `Chế độ: Thường` :
                                                        device.mode === 1 ? `Chế độ: Nhấp nháy` :
                                                            `Chế độ: Không xác định`
                                                }
                                            </p>
                                            <p>
                                                {
                                                    device.auto_mode ? `Tự động: Bật` : `Tự động: Tắt`
                                                }
                                            </p>
                                            <button className={style.btn_command} onClick={(e) => changeMode(e, "command", device.device_id)}>Thiết lập</button>

                                        </div>
                                    </>
                                ) : (
                                    <>
                                        <h4 className={style.title}>Camera: Không tín hiệu</h4>

                                        <div className={style.videoWrapper}>
                                            <div className={style.placeholder}>Không có dữ liệu</div>
                                        </div>

                                        <div className={style.info}>
                                            <p>⚫ Không xác định</p>
                                            <p>Số xe đang có: ❌</p>
                                            <p>Tổng xe: ❌</p>
                                            <p>Mức độ che phủ: ❌</p>
                                            <p>Chế độ: ❌</p>
                                            <p>Tự động: ❌</p>
                                            <button className={style.btn_command_unused}>Thiết lập</button>
                                        </div>
                                    </>
                                )}
                            </div>

                        );
                    })
                }
            </div>
            <div className={style.form_command} onClick={(e) => changeMode(e, null)} style={mode == "command" ? { display: "block" } : { display: "none" }}>
                <Form nameForm="Tạo thiết lập mới" fields={formPostCommand} onSubmit={handlePost} onChange={formPostChange} values={postCommandData} />
            </div>
        </div >
    );
}
export default TrafficMonitor;