'use server'
import { RegisterSchema, RegisterSchemaType } from '@/schema/registerSchema'
import { api } from '@/apiService/api'
import axios, { AxiosError } from 'axios'
import { logout } from '@/lib/session'
import { InstitutionRegisterSchema } from '@/schema/institutionRegisterSchema'

export interface RegisterResponse {
    error?: string
    token?: string
}

interface InstitutionRegisterResponse {
    access_token?: string
    refresh_token?: string
    error?: string
}

interface InstitutionRegisterRequest {
    name: string
    email: string
    password: string
    confirm_password: string
    credits: number
    hmac: string
}

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


export async function institutionRegister(data: InstitutionRegisterRequest): Promise<InstitutionRegisterResponse | undefined> {
    const validate = InstitutionRegisterSchema.safeParse(data)
    if (!validate.success) return { error: "Invalid Fields" }


    try {
        const res = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/institution/register/`, data)
        if (res.status !== 201) throw new AxiosError(res.data.email[0])
        return { access_token: res.data.access_token, refresh_token: res.data.refresh_token }
    } catch (e) {
        if (e instanceof AxiosError) {
            return { error: e.message || "An error occurred during registration" }
        }
    }
}


