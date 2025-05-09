'use server'
import { RegisterSchema, RegisterSchemaType } from '@/schema/registerSchema'
import { api } from '@/apiService/api'
import { AxiosError } from 'axios'
import { logout } from '@/lib/session'

export interface RegisterResponse {
    error?: string
    token?: string
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
