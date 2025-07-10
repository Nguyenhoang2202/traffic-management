const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
export const getDatas = async (skip = 0, limit = 20) => {
    const response = await fetch(`${BACKEND_URL}/datas/?skip=${skip}&limit=${limit}`, {
        method: 'GET',
        headers: {
            "Content-Type": 'application/json',
        }
    })
    if (!response.ok) {
        let errorMsg = "Get all traffic datas failed!";
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