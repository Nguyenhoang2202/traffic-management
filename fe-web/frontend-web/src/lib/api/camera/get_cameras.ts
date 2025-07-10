const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
export const getCameras = async () => {
    const response = await fetch(`${BACKEND_URL}/cameras/?limit=20`, {
        method: 'GET',
        headers: {
            "Content-Type": 'application/json',
        }
    })
    if (!response.ok) {
        let errorMsg = "Get all camera datas failed!";
        try {
            const err = await response.json();
            if (err.detail) {
                errorMsg = Array.isArray(err.detail)
                    ? err.detail.map((d: any) => d.msg || d || d).join(", ")
                    : err.detail;
            }
        } catch { }
        console.error(errorMsg)
        return null;
    }
    const data = await response.json();
    return data
}