"use client"
import Link from "next/link";
import style from "@/styles/header.module.scss"
import AccountMenu from "./AccountMenu";

// const navLink = [
//     { label: "", href: "" },
// ]
const Header = ({ display }: { display: () => void }) => {
    return (
        <header className={style.header}>
            <button onClick={display}>☰</button>

            <Link key="/" href="/dashboard/index">Traffic monitoring</Link>
            <div className={style.header_nav}>
                {/* {navLink.map(link => (
                <Link key={link.href} href={link.href}>{link.label}</Link>
            ))} */}
            </div>
            <AccountMenu />
        </header>
    )
}
export default Header