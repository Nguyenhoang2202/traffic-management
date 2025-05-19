"use client"
import style from "@/styles/accountMenu.module.scss"
import Link from "next/link"
import { useRouter } from "next/navigation"

const menuLink = [
    { label: "🗃️ Hồ sơ", href: "/dashboard/profile" },
    // { label: "⚙️ Setting", href: "/features/user" },
]
const AccountMenu = () => {
    const router = useRouter();
    const handleLogout = () => {
        console.log("Run Logout")

        document.cookie = "access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
        document.cookie = "token_type=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;";

        router.push("/auth/sign-in");
    }
    return (
        <div className={style.wrapper}>
            <div className={style.account}>👤</div>

            <div className={style.accountMenu}>
                {menuLink.map((item, index) => (
                    <Link className={style.menuItem} key={index} href={item.href}>
                        {item.label}
                    </Link>
                ))}
                <button onClick={handleLogout}>
                    ➡️ Đăng xuất
                </button>
            </div>
        </div>
    )
}
export default AccountMenu