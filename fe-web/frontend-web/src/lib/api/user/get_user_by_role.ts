import Cookies from 'js-cookie';
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
export const getUsersByRole = async (role: string, skip = 0, limit = 20) => {
    const access_token = Cookies.get("access_token");
    try {
        const response = await fetch(`${BACKEND_URL}/users/${role}?skip=${skip}&limit=${limit}`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${access_token}`,
            }
        });

        if (!response.ok) {
            const err = await response.json().catch(() => null);
            throw new Error(err?.detail || `Failed to fetch users by role ${role}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error in getUsersByRole:', error);
        return null;
    }
};