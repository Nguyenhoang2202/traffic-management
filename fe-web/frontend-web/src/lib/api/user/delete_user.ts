import Cookies from 'js-cookie';
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export const deleteUser = async (username: string) => {
    const access_token = Cookies.get("access_token");
    try {
        const response = await fetch(`${BACKEND_URL}/users/${username}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${access_token}`,
            },
        });

        if (!response.ok) {
            const err = await response.json().catch(() => null);
            const msg = err?.detail || `Failed to unactive user ${username}`;
            throw new Error(msg);
        }

        const data = await response.json();
        return data; // Trả về kết quả từ API
    } catch (error) {
        console.error('Error in unactiveUser:', error);
        return null;
    }
}