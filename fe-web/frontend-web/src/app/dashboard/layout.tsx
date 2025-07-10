// import "./globals.scss";
import ClientLayout from "@/components/layout/ClientLayout";
import "./dashboard-layout.scss";
export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <div className="dashboard-layout">
            <ClientLayout>{children}</ClientLayout>
        </div>
    )
}
