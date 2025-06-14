import axios from "axios"
import { BASE_URL } from "./api"


export interface IVerifyEmail {
    verifyEmailExists: (email: string) => Promise<boolean>
    resendVerificationEmail: (token?: string, email?: string, name?: string) => Promise<string>
    verifyEmail: (otp: number, email: string) => Promise<boolean>
}

// Institution Verification
export const institutionSendVerificationEmail = async (email?: string, name?: string): Promise<string> => {
    const res = await axios.post(`${BASE_URL}/auth/institution-resend-verification-email/`, { email, name }, { validateStatus: status => status < 500 })

    if (res.status === 200) return res.data.message
    throw new Error(res.data.message || "Failed to send verification email")
}

export const institutionVerifyEmailExists = async (email: string): Promise<boolean> => {
    const res = await axios.get(`${BASE_URL}/auth/institution-verify-email/${email}/`, { validateStatus: status => status < 500 })

    if (res.status === 200) return true
    throw new Error(res.data.message || "Invalid email")
}

export const institutionVerifyEmail = async (otp: number, email: string): Promise<boolean> => {
    const res = await axios.post(`${BASE_URL}/auth/institution-verify-email/${email}/`, { otp }, { validateStatus: status => status < 500 })

    if (res.status === 200) return true
    throw new Error(res.data.message || "Failed to verify email")
}

// User Verification
export const verifyEmailToken = async (token: string): Promise<boolean> => {
    const res = await axios.get(`${BASE_URL}/auth/verify-email/${token}/`, { validateStatus: status => status < 500 })

    if (res.status === 200) return true
    throw new Error("Invalid token")
}

export const verifyEmail = async (otp: number, token: string): Promise<boolean> => {
    const url = `${BASE_URL}/auth/verify-email/${token}/`
    const res = await axios.post(url, { otp }, { validateStatus: status => status < 500 })

    if (res.status === 200) return true
    throw new Error(res.data.detail)
}

export const resendEmail = async (token?: string, email?: string): Promise<string> => {
    // 1. Token has expired, 2. Sending a new verification request
    const url = token ? `${BASE_URL}/auth/resend-verification-email/${token}/` : `${BASE_URL}/auth/resend-verification-email/`
    const res = await axios.post(url, { email }, { validateStatus: status => status < 500 })

    if (res.status === 200) return res.data.token
    throw new Error(res.data.message || "Failed to resend email")
}

export const institutionVerificationService: IVerifyEmail = {
    resendVerificationEmail: institutionSendVerificationEmail,
    verifyEmailExists: institutionVerifyEmailExists,
    verifyEmail: institutionVerifyEmail,
}

export const userVerificationService: IVerifyEmail = {
    resendVerificationEmail: resendEmail,
    verifyEmailExists: verifyEmailToken,
    verifyEmail: verifyEmail,
}