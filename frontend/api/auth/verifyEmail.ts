import { api } from "@/lib/api"
import { redirect } from "next/navigation"

export const verifyEmailToken = async (token: string): Promise<boolean> => {
    const res = await api.get(`/auth/verify-email/${token}/`)

    if (res.status === 200) return true

    throw new Error("Invalid token")
}


export const verifyEmail = async (otp: number, token: string): Promise<boolean> => {
    const res = await api.post(`/auth/verify-email/${token}/`, {
        otp
    })
    if (res.status === 200) return true

    throw new Error(res.data.detail)
}

export const resendEmail = async (email?: string, token?: string) => {
    const url = token ? `/auth/resend-verification-email/${token}/` : "/auth/resend-verification-email/"
    const res = await api.post(url, { email })

    if (res.status === 200) return res.data.token
    if (res.status === 403) return redirect('/login')

    throw new Error(res.data.message || "Failed to resend email")
}
