import Cookies from 'js-cookie';
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

// 1. Cập nhật thông tin user hiện tại (không gồm role, pass)
export async function updateCurrentUser(userData: any) {
    const access_token = Cookies.get("access_token");
    const res = await fetch(`${BACKEND_URL}/users/me/`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${access_token}`,
        },
        body: JSON.stringify(userData),
    });

    if (!res.ok) {
        throw new Error(`Update failed: ${res.statusText}`);
    }

    return await res.json();
}

// 2. Cập nhật mật khẩu user hiện tại
export async function updateCurrentUserPassword(userPasswordData: any) {
    const access_token = Cookies.get("access_token");
    const res = await fetch(`${BACKEND_URL}/users/me/password/`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${access_token}`,
        },
        body: JSON.stringify(userPasswordData),
    });

    if (!res.ok) {
        throw new Error(`Password update failed: ${res.statusText}`);
    }

    return await res.json();
}

// 3. Admin cập nhật role cho user khác
export async function updateUserRole(username: string, role: string) {
    const access_token = Cookies.get("access_token");
    const res = await fetch(`${BACKEND_URL}/users/role/${username}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${access_token}`,
        },
        body: JSON.stringify({ role }),  // ✅ key phải là 'role' đúng theo schema backend
    });
    console.log(JSON.stringify({ role }));
    if (!res.ok) {
        throw new Error(`Role update failed: ${res.statusText}`);
    }

    return await res.json();
}
