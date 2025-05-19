const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export const downloadExcelData = async (device_id: string, skip = 0, limit = 100) => {
    try {
        const response = await fetch(`${BACKEND_URL}/datas/export/${device_id}?skip=${skip}&limit=${limit}`, {
            method: 'GET',
        });
        if (!response.ok) {
            let errorMsg = "Export Excel failed!";
            try {
                const err = await response.json();
                if (err.detail) {
                    errorMsg = Array.isArray(err.detail)
                        ? err.detail.map((d: any) => d.msg || d || d).join(", ")
                        : err.detail;
                }
            } catch { }
            console.error(errorMsg);
            return;
        }

        // Nhận blob dữ liệu từ backend
        const blob = await response.blob();

        // Tạo URL từ blob
        const url = window.URL.createObjectURL(blob);

        // Tạo thẻ <a> để tải file
        const a = document.createElement('a');
        a.href = url;
        a.download = `traffic_data_camera_${device_id}.xlsx`; // Tên file tải về
        document.body.appendChild(a);
        a.click();

        // Dọn dẹp
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (err) {
        console.error("Export request error:", err);
    }
};
