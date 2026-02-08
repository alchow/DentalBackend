import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
    // Redirect root path to /schedule
    if (request.nextUrl.pathname === '/') {
        return NextResponse.redirect(new URL('/schedule', request.url))
    }
}

export const config = {
    matcher: '/',
}
