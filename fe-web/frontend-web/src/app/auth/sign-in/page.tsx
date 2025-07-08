"use client"
import { signin } from "@/lib/api/auth/sign-in";
import { useRouter } from "next/navigation";
import { useState } from "react";
import style from "./sign-in.module.scss";
import Link from "next/link";
import Form, { FieldType } from "@/components/common/Form";
const formSignIn = [
    { name: 'username', type: "text" as FieldType, label: 'Username', },
    { name: 'password', type: "password" as FieldType, label: 'Password', }
];


const SignIn = () => {
    const router = useRouter();

    const [formData, setFormData] = useState<Record<string, string>>(
        formSignIn.reduce((acc, field) => (
            { ...acc, [field.name]: "" }
        ), {})
    );
    const HandleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault(); // Ngăn reload page
        const Data = formData;
        if (!Data.username || !Data.password) {
            alert("Vui lòng nhập đầy đủ thông tin!");
            return;
        }
        const success = await signin(Data);
        if (success) {
            console.log("Đăng nhập thành công");
            router.push('/dashboard/index'); // Chuyển hướng sau khi đăng nhập thành công
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
            <Form nameForm="Sign in" fields={formSignIn} onSubmit={HandleSubmit} onChange={handleChange} values={formData} />
            <p>Don't you have an account yet? <Link href="/auth/sign-up">Sign up</Link></p>
        </div>
    )
}
export default SignIn;