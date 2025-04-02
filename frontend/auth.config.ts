import type { NextAuthConfig } from "next-auth"
import Credentials from "next-auth/providers/credentials"
import axios, { AxiosError } from 'axios'
import { LoginSchema } from "./schema/loginSchema";
import { loginAccessSchema } from "./schema/loginAccessSchema";
import type { ILogin } from "./types/auth.type"
import Google from "next-auth/providers/google";


class APIError extends Error {
    constructor(message: string, public status: number) {
        super(message);
        this.name = 'APIError';
    }
}

export default {
    providers: [
        Google,
        Credentials({
            id: "access-code",
            name: "Access Code",
            credentials: {
                accessCode: { label: "Access Code", type: "text" },
                nationalId: { label: "National ID", type: "number" },
            },
            async authorize(credentials) {
                const validate = loginAccessSchema.safeParse({ accessCode: credentials.accessCode, nationalId: credentials.nationalId })
                if (!validate.success) return null

                const { accessCode, nationalId } = validate.data

                try {
                    const response = await axios.post(`${process.env.API_URL}/auth/login-access/`, { access_code: accessCode, national_id: nationalId })
                    return response.data
                } catch (error) {
                    if (error instanceof AxiosError) {
                        return { error: error.response?.data.detail }
                    }
                }
                throw new APIError("Something went wrong", 500);

            }

        }),
        Credentials({
            id: "email",
            name: "Email",
            credentials: {
                email: { label: "Email", type: "email" },
                password: { label: "Password", type: "password" },
            },
            async authorize(credentials) {
                const validate = LoginSchema.safeParse({ email: credentials.email, password: credentials.password })
                if (!validate.success) return null

                try {
                    const response = await axios.post(`${process.env.API_URL}/auth/login/`, validate.data)
                    console.log("RESPONSE", response.data)

                    // The data is bind the user object defined in the auth.ts file
                    return response.data
                } catch (error) {
                    if (error instanceof AxiosError) {
                        return { error: error.response?.data.detail }
                    }
                }
            }
        })
    ]
} satisfies NextAuthConfig;

