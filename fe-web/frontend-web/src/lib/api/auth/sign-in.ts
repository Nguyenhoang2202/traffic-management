const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
export const signin = async (payload: any) => {         // bắt buộc
    try {
        const response = await fetch(BACKEND_URL + '/users/login', {
            method: 'POST',
            headers: {
                "Content-Type": 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            let errorMsg = "Sign in failed!";
            try {
                const err = await response.json();
                if (err.detail) {
                    errorMsg = Array.isArray(err.detail)
                        ? err.detail.map((d: any) => d.msg || d || d).join(", ")
                        : err.detail;
                }
            } catch { }
            console.error(errorMsg)
            return null; // Đăng nhập không thành công
        }

        const data = await response.json();
        const { access_token, token_type } = data;
        document.cookie = `access_token=${access_token}; path=/; SameSite=Strict`;
        document.cookie = `token_type=${token_type}; path=/; SameSite=Strict`;

        return true; // Đăng nhập thành công


    }
    catch (error) {
        console.error('Error:', error)
        return null;
    }
}