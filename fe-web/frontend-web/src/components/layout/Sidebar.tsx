import Link from "next/link"
import style from "@/styles/sidebar.module.scss"
const navLink = [
    { label: "Trang chủ", href: "/dashboard/index" },
    { label: "Dữ liệu giao thông", href: "/dashboard/traffic-data" },
    { label: "Camera", href: "/dashboard/camera" },
    { label: "Người dùng", href: "/dashboard/user" },
    { label: "Các điều chỉnh", href: "/dashboard/command" },
]

interface SidebarProps {
    isDisplay: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ isDisplay }) => {
    return (
        <div className={`${style.sidebar} ${!isDisplay ? style.close : ""}`}>
            <div className={style.list_link}>
                {navLink.map(link => (
                    <Link key={link.href} href={link.href}>{link.label}</Link>
                ))}
            </div>
        </div>
    )
}
export default Sidebar