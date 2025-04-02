'use server'
import { type LoginSchemaType, LoginSchema } from '@/schema/loginSchema'
import { AuthError } from 'next-auth'
import { signIn } from '@/auth'
import { LoginError } from '@/types/auth.type'


export async function login(data: LoginSchemaType): Promise<LoginError | undefined> {
    const validate = LoginSchema.safeParse(data)
    if (!validate.success) return { message: "Invalid Fields", type: "CredentialsSignin" }

    const { email, password } = validate.data

    try {
        const res = await signIn('email', {
            email,
            password,
        });
        console.log("RESPONSE ERROR", res)
    } catch (error) {
        if (error instanceof Error) {
            console.log("CUTOMERROR", error)
            return { message: error.message }
        }
        // if (error instanceof AuthError) {
        //     console.log('@Error', error)
        //     switch (error.type) {
        //         case "CredentialsSignin":
        //             return { message: "Invalid credentials", type: "CredentialsSignin" }
        //         case "Verification":
        //             return { message: "Email is not Verified", type: "Verification" }
        //         default:
        //             return { message: error.message }
        //     }
        // }
        // return null
        throw error
    }

}

