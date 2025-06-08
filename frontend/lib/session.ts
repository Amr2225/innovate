'use server'
import jwt from 'jsonwebtoken'
import { cookies } from 'next/headers'
import { ITokens, Session, ITokenClaims } from '@/types/auth.type'
import { User } from '@/types/user.types'

const COOKIES_CONFIG = {
    maxAge: 60 * 60 * 24 * 7, // 1 week
    path: "/",
    // domain: process.env.HOST ?? "localhost",
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax" as const
}

export const setSession = async (name: string, tokens: ITokens) => {
    const cookieStore = await cookies();
    cookieStore.set(name, JSON.stringify(tokens), COOKIES_CONFIG);
}

const getCookie = async (name: string): Promise<ITokens | null> => {
    const cookieStore = await cookies();
    const session = cookieStore.get(name)?.value
    return session ? JSON.parse(session) : null
}

export const getSession = async (): Promise<Session | null> => {
    const session = await getCookie("innovate-auth")
    if (session?.accessToken) {
        const tokenClaims = jwt.decode(session.accessToken) as ITokenClaims
        const user: User = {
            id: tokenClaims?.user_id,
            email: tokenClaims?.email,
            name: tokenClaims?.name,
            role: tokenClaims?.role,
            credits: tokenClaims?.credits,
            profile_picture: `${process.env.NEXT_PUBLIC_API_URL}${tokenClaims?.profile_picture}`
        }
        return { user, accessToken: session.accessToken, refreshToken: session.refreshToken, exp: tokenClaims.exp }
    }
    return null
}


export const logout = async () => {
    const cookieStore = await cookies();
    cookieStore.delete("innovate-auth")
}
