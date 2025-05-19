'use client'
import style from '@/styles/client.module.scss'
import { useState } from 'react'
import Header from './Header'
import Sidebar from './Sidebar'
import Footer from './Footer'
import { usePathname } from 'next/navigation'

const ClientLayout = ({ children }: { children: React.ReactNode }) => {
    const pathname = usePathname();
    const isAuth = pathname.startsWith('/auth');
    const [display, setDisplay] = useState(false)
    if (isAuth) return <>{children}</>;
    return (
        <>
            <Header display={() => setDisplay(!display)} />
            <div className={style.content}>
                <Sidebar isDisplay={display} />
                <div className={style.main_content}>
                    {children}
                </div>
            </div>
            <Footer />
        </>
    );
}

export default ClientLayout