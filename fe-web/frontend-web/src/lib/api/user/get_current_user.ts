import Cookies from 'js-cookie';
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export const getCurrentUser = async () => {
    const access_token = Cookies.get("access_token");
    try {
        const response = await fetch(`${BACKEND_URL}/users/current_user/`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${access_token}`,
            }
        });

        if (!response.ok) {
            const err = await response.json().catch(() => null);
            throw new Error(err?.detail || 'Failed to fetch current user');
        }

        return await response.json();
    } catch (error) {
        console.error('Error in getCurrentUser:', error);
        return null;
    }
};