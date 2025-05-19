import { NextResponse, NextRequest } from "next/server";
import path from "path";

const PUBLIC_PATHs = ['sign-in', 'sign-up']

function parseJwt(token: string) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function (c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        return null;
    }
}


export function middleware(request: NextRequest) {
    const token = request.cookies.get("access_token")?.value;
    const { pathname } = request.nextUrl

    if (PUBLIC_PATHs.some(path => pathname.includes(path))) {
        return NextResponse.next()
    }

    if (!token) {
        const loginUrl = request.nextUrl.clone()
        loginUrl.pathname = '/auth/sign-in'
        return NextResponse.redirect(loginUrl)
    }

    const payload = parseJwt(token);
    const now = Math.floor(Date.now() / 1000);

    if (payload?.exp && payload.exp < now) {
        const loginUrl = request.nextUrl.clone();
        loginUrl.pathname = '/auth/sign-in';
        return NextResponse.redirect(loginUrl);
    }

    return NextResponse.next()
}
export const config = {
    matcher: [
        /*
          Áp dụng middleware cho tất cả các trang trừ:
          - `/auth/sign_in`
          - `/auth/sign_up`
          - Các file tĩnh (như _next/static)
        */
        "/((?!_next/static|_next/image|favicon.ico).*)",
    ],
};