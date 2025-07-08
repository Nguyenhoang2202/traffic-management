const BACKEND_URL = process.env.NEXT_PUBLIC_WS_BACKEND_URL;

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

interface WebSocketMessage {
    type: "batch_detect";
    data: DeviceData[];
}

type OnMessageCallback = (data: DeviceData[]) => void;

export class WebSocketClient {
    private socket: WebSocket | null = null;
    private onMessage: OnMessageCallback;
    private reconnectDelay = 2000;
    private page: number;
    private pageSize: number;
    private shouldReconnect = true;

    constructor(onMessage: OnMessageCallback, page: number = 1, pageSize: number = 4) {
        this.page = page;
        this.pageSize = pageSize;
        this.onMessage = onMessage;

        this.connect();
    }

    private connect() {
        if (!BACKEND_URL || !BACKEND_URL.startsWith("ws")) {
            console.error("BACKEND_URL is not defined or invalid:", BACKEND_URL);
            return;
        }

        const url = `${BACKEND_URL}/ws/fe?page=${this.page}&page_size=${this.pageSize}`;
        this.socket = new WebSocket(url);

        this.socket.onopen = () => {
            console.log("WebSocket connected to /ws/fe");
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
            // Không tự đóng, cứ để socket.onclose lo reconnect
        };

        this.socket.onclose = (event) => {
            console.warn(`WebSocket closed (code: ${event.code}). Reconnecting in ${this.reconnectDelay}ms...`);
            if (this.shouldReconnect) {
                setTimeout(() => this.connect(), this.reconnectDelay);
            }
        };
    }

    /**
     * Chỉ gọi khi muốn đóng thủ công — ví dụ khi user logout
     */
    closeManually() {
        console.log("🔌 WebSocket manually closed.");
        this.shouldReconnect = false;
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.close(1000, "Closed by client");
        }
    }
}
