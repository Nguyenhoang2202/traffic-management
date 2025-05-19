"use client"
import { signup } from "@/lib/api/auth/sign-up";
import { useRouter } from "next/navigation";
import { useState } from "react";
import style from "./sign-up.module.scss";
import Link from "next/link";
import Form from "@/components/common/Form";

const formSignIn = [
    { name: 'username', type: 'text', label: 'Username', },
    { name: 'email', type: 'email', label: 'Email', },
    { name: 'password', type: 'password', label: 'Password', }
];


const SignUp = () => {
    const router = useRouter();

    const [formData, setFormData] = useState<Record<string, string>>(
        formSignIn.reduce((acc, field) => (
            { ...acc, [field.name]: "" }
        ), {})
    );
    const HandleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault(); // Ngăn reload page
        const Data = formData;
        if (!Data.username || !Data.password || !Data.email) {
            alert("Vui lòng nhập đầy đủ thông tin!");
            return;
        }
        const success = await signup(Data);
        if (success) {
            console.log("Đăng ký thành công");
            router.push('/dashboard/index'); // ✅ Chuyển hướng sau khi đăng nhập thành công
        }
    };

    const handleChange = (e: any) => {
        const { name, value } = e.target;
        setFormData((prevData) => ({
            ...prevData,
            [name]: value,
        }));
    };

    return (
        <div className={style.form_signin}>
            <Form nameForm="Sign up" fields={formSignIn} onSubmit={HandleSubmit} onChange={handleChange} values={formData} />
        </div>
    )
}
export default SignUp;