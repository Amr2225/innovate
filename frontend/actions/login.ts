'use server'
import { setSession } from '@/lib/session'
import axios, { AxiosError } from 'axios'
import jwt from 'jsonwebtoken'

// Types
import { type LoginSchemaType, LoginSchema } from '@/schema/loginSchema'
import { User } from '@/types/user.types'
import { ILogin, LoginResponse } from '@/types/auth.type'


export async function login(data: LoginSchemaType): Promise<LoginResponse> {
    const validate = LoginSchema.safeParse(data)
    if (!validate.success) return { error: "Invalid Fields", type: "CredentialsSignin" }

    const { email, password } = validate.data

    try {
        const res = await axios.post<ILogin>(`${process.env.NEXT_PUBLIC_API_URL}/auth/login/`, { email, password })
        await setSession("innovate-auth", { accessToken: res.data.access, refreshToken: res.data.refresh })

        const user = jwt.decode(res.data.access) as User
        return { role: user.role }
    } catch (error) {
        if (error instanceof AxiosError) {
            if (error.response?.status === 401)
                return { error: "Invalid Credentials", type: "CredentialsSignin" }
            if (error.response?.status === 403)
                return { error: "Email not verified", type: "Verification" }
            if (error.response?.status === 451)
                return { error: "Account is suspended, Please contact your institution", type: "ActiveAccount" }
        }
        return { error: "Something went wrong", type: "CredentialsSignin" }
    }
} 
