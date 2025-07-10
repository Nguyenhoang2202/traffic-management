import Link from "next/link"
import style from "@/styles/footer.module.scss"
type typeLink = { type: "link", label: string, href: string }
type typeText = { type: "text", label: string, cont: string }

type footerItem = typeLink | typeText
type footerSection = {
    title: string,
    items: footerItem[],
}



const footerSections: footerSection[] = [
    {
        title: "About",
        items: [
            { type: "text", label: "Name", cont: "Nguyễn Tiến Hoàng" },
            { type: "text", label: "Adress", cont: "Phạm Kham - Lạc Hồng - Văn Lâm - HƯng Yên" },
            { type: "text", label: "Contract", cont: "0862355898" },
            { type: "text", label: "Email", cont: "nguyentienhoang2202@gmail.com" },
            { type: "link", label: "Github", href: "https://github.com/Nguyenhoang2202" },
        ]
    },
    {
        title: "Social",
        items: [
            { type: "link", label: "Youtube", href: "/youtube" },
            { type: "link", label: "Facebook", href: "/facebook" },
        ]
    }
]

const Footer = () => {
    return (
        <footer className={style.footer}>
            {footerSections.map(section => (
                <div className={style.footer_section} key={section.title}>
                    <h4>{section.title}</h4>
                    <ul>
                        {section.items.map((item, idx) => (
                            <li key={idx}>
                                {item.type === "link" ? (<>{item.label}: < Link href={item.href}>Here</Link></>) : (<span>{item.label}: {item.cont}</span>)}
                            </li>
                        ))}
                    </ul>
                </div>
            ))
            }
        </footer >
    )
}
export default Footer