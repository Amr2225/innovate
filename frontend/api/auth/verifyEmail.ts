import axios from "axios"

export const verifyEmailToken = async (token: string): Promise<boolean> => {
    const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/auth/verify-email/${token}/`, { validateStatus: status => status < 500 })

    if (res.status === 200) return true
    throw new Error("Invalid token")
}


export const verifyEmail = async (otp: number, token: string): Promise<boolean> => {
    const url = `${process.env.NEXT_PUBLIC_API_URL}/auth/verify-email/${token}/`
    const res = await axios.post(url, { otp }, { validateStatus: status => status < 500 })

    if (res.status === 200) return true
    throw new Error(res.data.detail)
}

export const resendEmail = async (email?: string, token?: string) => {
    // 1. Token has expired, 2. Sending a neew verification request
    const url = token ? `${process.env.NEXT_PUBLIC_API_URL}/auth/resend-verification-email/${token}/` : `${process.env.NEXT_PUBLIC_API_URL}/auth/resend-verification-email/`
    const res = await axios.post(url, { email }, { validateStatus: status => status < 500 })

    if (res.status === 200) return res.data.token
    throw new Error(res.data.message || "Failed to resend email")
}
