import Cookies from 'js-cookie';
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
const getToken = () => Cookies.get("access_token");
export const getCommandsByUser = async (userId: string) => {
    const token = getToken();
    if (!token) throw new Error("Không tìm thấy token");

    const res = await fetch(`${BACKEND_URL}/commands/${userId}`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || `Không thể lấy commands của user ${userId}`);
    }

    return await res.json(); // Trả về danh sách commands của user đó
};
