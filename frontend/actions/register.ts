'use server'
import { signOut } from '@/auth'
import { RegisterSchema, RegisterSchemaType } from '@/schema/registerSchema'
import api from '@/lib/api'
import { AxiosError } from 'axios'
import { LoginError } from '@/types/auth.type'

export async function register(data: RegisterSchemaType): Promise<LoginError | undefined> {
    const validate = RegisterSchema.safeParse(data)
    if (!validate.success) return { message: "Invalid Fields" }

    try {
        const res = await api.post('/auth/add-credentials/', validate.data)
        console.log("registration data", res.data)
        if (res.status !== 201) throw new AxiosError(res.data.email[0])
        return undefined
    } catch (e) {
        if (e instanceof AxiosError) {
            if (e.response?.status === 401) {
                await signOut()
                return { message: "Unauthorized access" }
            }
            // Return the error message from the backend if available
            return {
                message: e.message || "An error occurred during registration",
                type: "RegistrationError"
            }
        }

        return { message: "An unexpected error occurred" }
    }
}
