'use server'
import { type LoginAccessSchemaType, loginAccessSchema } from '@/schema/loginAccessSchema'
import { signIn } from '@/auth'
import { LoginError } from '@/types/auth.type'
// import { APIError } from '@/errors/auth.error'
import { AuthError } from 'next-auth'


export async function loginAccess(data: LoginAccessSchemaType): Promise<LoginError | undefined> {
    const validate = loginAccessSchema.safeParse(data)
    if (!validate.success) return { message: "Invalid Fields", type: "CredentialError" }

    const { accessCode, nationalId } = validate.data

    try {
        await signIn('access-code', {
            accessCode,
            nationalId,
        });
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
        if (error instanceof AuthError) {
            return { message: error.message, type: error.type as LoginError['type'] }
        }
        // return { message: "Something went wrong", type: "CredentialError" }
        return;
        throw error
    }
}

