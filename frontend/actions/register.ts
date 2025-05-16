'use server'
import { RegisterSchema, RegisterSchemaType } from '@/schema/registerSchema'
import { api } from '@/apiService/api'
import axios, { AxiosError } from 'axios'
import { logout, setSession } from '@/lib/session'
import { ILogin } from '@/types/auth.type'

export interface RegisterResponse {
    error?: string
    token?: string
}

interface InstitutionRegisterResponse {
    error?: string
    isSuccess: boolean
}

// interface InstitutionRegisterRequest {
//     name: string
//     email: string
//     password: string
//     confirm_password: string
//     credits: number
//     logo: string
//     hmac: string
// }

export async function register(data: RegisterSchemaType): Promise<RegisterResponse | undefined> {
    const validate = RegisterSchema.safeParse(data)
    if (!validate.success) return { error: "Invalid Fields" }

    try {
        const res = await api.post('/auth/add-credentials/', validate.data)
        if (res.status !== 201) throw new AxiosError(res.data.email[0])
        return { token: res.data.token }
    } catch (e) {
        if (e instanceof AxiosError) {
            if (e.response?.status === 401) {
                await logout()
                return { error: "Unauthorized access" }
            }
            // Return the error message from the backend if available
            return {
                error: e.message || "An error occurred during registration",
            }
        }

        return { error: "An unexpected error occurred" }
    }
}


export async function institutionRegister(data: FormData): Promise<InstitutionRegisterResponse | undefined> {
    try {
        const res = await axios.post<ILogin>(`${process.env.NEXT_PUBLIC_API_URL}/institution/register/`, data, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
        await setSession("innovate-auth", { accessToken: res.data.access, refreshToken: res.data.refresh })
        return { isSuccess: true }
    } catch (e) {
        if (e instanceof AxiosError) {
            console.log("Reigster error", e.response?.data)
            return { isSuccess: false, error: "Registration Failed" }
        }
    }
}


