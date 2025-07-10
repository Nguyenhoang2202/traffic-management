import './authLayout.scss';
export default function AuthLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    console.log("AuthLayout!")
    return (
        <div className="auth_layout">
            {children}
        </div>
    )
}