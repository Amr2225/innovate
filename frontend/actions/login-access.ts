'use server'
import axios, { AxiosError } from 'axios'
import { setSession } from '@/lib/session'
import jwt from 'jsonwebtoken'

// Types
import { type LoginAccessSchemaType, loginAccessSchema } from '@/schema/loginAccessSchema'
import { LoginResponse } from '@/types/auth.type'
import { User } from '@/types/user.types'


export async function loginAccess(data: LoginAccessSchemaType): Promise<LoginResponse | undefined> {
    const validate = loginAccessSchema.safeParse(data)
    if (!validate.success) return { error: "Invalid Fields", type: "CredentialsSignin" }

    const { accessCode, nationalId } = validate.data

    try {
        const res = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/auth/login-access/`, { access_code: accessCode, national_id: nationalId })
        await setSession("innovate-auth", { accessToken: res.data.access, refreshToken: res.data.refresh })

        const user = jwt.decode(res.data.access) as User
        return { role: user.role, isFirstLogin: true }
    } catch (error) {
        if (error instanceof AxiosError) {
            if (error.status === 401 || error.response?.status === 400) return { error: "Invalid Credentials", type: "CredentialsSignin" }
            if (error.status === 403) return { error: "Email not verified", type: "Verification" }
            if (error.status === 451) return { error: "Account is suspended, Please contact your institution", type: "ActiveAccount" }
        }
    }
}

