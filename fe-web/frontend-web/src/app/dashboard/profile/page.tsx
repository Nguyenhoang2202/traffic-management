"use client";
import { getCurrentUser } from "@/lib/api/user/get_current_user"
import { updateCurrentUser, updateCurrentUserPassword } from "@/lib/api/user/put_user"
import style from "@/app/dashboard/profile/profile.module.scss"
import { useState, useEffect } from "react";
import Form from "@/components/common/Form";
import type { FieldType } from "@/components/common/Form";

interface userResponse {
    id: string;
    username: string;
    email: string;
    role: string;
    created_at: Date;
}
// Import FieldType from your Form component

const userForm = [
    { name: 'username', type: 'text' as FieldType, label: 'Tên người dùng', },
    { name: 'email', type: 'text' as FieldType, label: 'Email', },
];
const userPasswordForm = [
    { name: 'old_password', type: 'text' as FieldType, label: 'Mật khẩu cũ', },
    { name: 'new_password', type: 'text' as FieldType, label: 'Mật khẩu mới', },
];
const Profile = () => {
    const [user, setUser] = useState<userResponse>();
    const [mode, setMode] = useState<"up_profile" | "up_password" | null>(null)
    // Lưu trữ dữ liệu từ form
    const [userFormData, setUserFormData] = useState<Record<string, string>>(
        userForm.reduce((acc, field) => (
            { ...acc, [field.name]: "" }
        ), {})
    );
    const [userPasswordFormData, setUserPasswordFormData] = useState<Record<string, string>>(
        userPasswordForm.reduce((acc, field) => (
            { ...acc, [field.name]: "" }
        ), {})
    );
    //  Quản lý sự thay đổi dữ liệu
    const handleChangeUserForm = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setUserFormData((prevData) => ({
            ...prevData, [name]: value,
        }));
    };
    const handleChangeUserPassword = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setUserPasswordFormData((prevData) => ({
            ...prevData, [name]: value,
        }));
    };
    // PUT User
    // Set form put user
    const getUserToPut = async () => {
        try {
            if (user) {
                setUserFormData({ username: user.username, email: user.email });
            }
        } catch (error) {
            console.error("Error:", error);
        }
    }
    // Handle put user
    const handlePutUser = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const Data = userFormData;
        try {
            const newUserProfile = await updateCurrentUser(Data);
            if (newUserProfile.detail) {
                alert(newUserProfile.detail);
            }
            else {
                alert("Thay đổi thông tin thành công!");
                setUser(newUserProfile);
            }
        } catch (error) {
            console.error("Error:", error);
        }
    };
    // Handle put user Password
    const handlePutUserPassword = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const Data = userPasswordFormData;
        try {
            const Response = await updateCurrentUserPassword(Data);
            if (Response.detail) {
                alert(Response.detail);
            }
            else {
                alert(Response.mesager);
                setUserPasswordFormData({ old_password: "", new_password: "" });
            }
        } catch (error) {
            console.error("Error:", error);
        }
    };
    // Get user profile fist time 
    useEffect(() => {
        const getUser = async () => {
            try {
                const data = await getCurrentUser();
                setUser(data);
            } catch (error) {
                console.error(error);
            }
        }
        getUser();
    }, []);
    const changeMode = (e: React.MouseEvent<HTMLElement>, mode: "up_profile" | "up_password" | null) => {
        if (e.target != e.currentTarget) {
            return;
        }
        setMode(mode);
    }
    return (
        <div className={style.container}>
            <h1 className={style.title}>Thông tin người dùng</h1>
            <div className={style.userBoard}>
                {user ? (
                    <>
                        <p>ID: {user.id}</p>
                        <p>Họ tên: {user.username}</p>
                        <p>Email: {user.email}</p>
                        <p>Quyền: {user.role}</p>
                        <p>Thời điểm tạo: {user.created_at.toLocaleString()}</p>
                        {/* Hiển thị thêm các thông tin nếu có */}
                    </>
                ) : (
                    <p>Đang tải thông tin người dùng...</p>
                )}
            </div>
            <button className={style.ptn_put_user} onClick={(e) => { changeMode(e, "up_profile"); getUserToPut() }}>Thay đổi thông tin</button>
            <button className={style.btn_put_password} onClick={(e) => changeMode(e, "up_password")}>Đổi mật khẩu</button>

            <div className={style.form} onClick={(e) => changeMode(e, null)} style={mode == "up_profile" ? { display: "block" } : { display: "none" }}>
                <Form nameForm="Đổi thông tin" fields={userForm} onSubmit={handlePutUser} onChange={handleChangeUserForm} values={userFormData} />
            </div>
            <div className={style.form} onClick={(e) => changeMode(e, null)} style={mode == "up_password" ? { display: "block" } : { display: "none" }}>
                <Form nameForm="Đổi mật khẩu" fields={userPasswordForm} onSubmit={handlePutUserPassword} onChange={handleChangeUserPassword} values={userPasswordFormData} />
            </div>
        </div>
    );
}
export default Profile