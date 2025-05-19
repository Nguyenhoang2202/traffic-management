import Cookies from 'js-cookie';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
const getToken = () => Cookies.get("access_token");
export const createCommand = async (commandData: any) => {
    const token = getToken();
    if (!token) throw new Error("Không tìm thấy token");

    const res = await fetch(`${BACKEND_URL}/commands/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(commandData),
    });

    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Tạo command thất bại");
    }

    return await res.json(); // Trả về command vừa tạo
};
