const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
export const signup = async (data: any) => {
    const response = await fetch(BACKEND_URL + '/users/', {
        method: 'POST',
        headers: {
            "Content-Type": 'application/json',
        },
        body: JSON.stringify(data),
    });
    if (!response.ok) {
        let errorMsg = "Sign up failed!";
        try {
            const err = await response.json();
            if (err.detail) {
                errorMsg = Array.isArray(err.detail)
                    ? err.detail.map((d: any) => d.msg || d || d).join(", ")
                    : err.detail;
            }
        } catch { }
        console.error(errorMsg)
        return null; // Đăng ký không thành công
    }
    const dataResponse = await response.json();
    const { access_token, token_type } = dataResponse;
    document.cookie = `access_token=${access_token}; path=/; SameSite=Strict`;
    document.cookie = `token_type=${token_type}; path=/; SameSite=Strict`;
    return true; // Đăng ký thành công
    // return dataResponse; // Đăng ký thành công, trả về dữ liệu người dùng
}