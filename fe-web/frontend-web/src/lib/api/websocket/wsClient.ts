// wsClient.ts
const BACKEND_URL = process.env.NEXT_PUBLIC_WS_BACKEND_URL;

interface DeviceData {
    light_state: number;
    remaining_time: number;
    device_id: string;
    img_detected: string; // base64 image
    num_current: number;
    num_total: number;
    cover_ratio: number;
    mode: number;
    auto_mode: number;
}

interface WebSocketMessage {
    type: "batch_detect";
    data: DeviceData[];
}

type OnMessageCallback = (data: DeviceData[]) => void;

export class WebSocketClient {
    private socket: WebSocket | null = null;
    private onMessage: OnMessageCallback;

    constructor(onMessage: OnMessageCallback, page: number = 1, pageSize: number = 4) {
        const url = `${BACKEND_URL}/ws/fe?page=${page}&page_size=${pageSize}`;
        this.onMessage = onMessage;
        this.socket = new WebSocket(url);

        this.socket.onopen = () => {
            console.log("✅ WebSocket connected to /ws/fe");
        };

        this.socket.onmessage = (event) => {
            try {
                const message: WebSocketMessage = JSON.parse(event.data);
                if (message.type === "batch_detect") {
                    this.onMessage(message.data);
                }
            } catch (error) {
                console.error("Failed to parse WebSocket message", error);
            }
        };

        this.socket.onerror = (error) => {
            console.error("WebSocket error", error);
        };

        this.socket.onclose = () => {
            console.log("WebSocket connection closed");
        };
    }

    close() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.close();
        }
    }
}
