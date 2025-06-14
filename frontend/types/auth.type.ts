import { Role, User } from "./user.types";

export interface ILogin {
    refresh: string;
    access: string;
}

export type ErrorType = "CredentialsSignin" | "Verification" | "ActiveAccount"

export interface LoginError {
    message: string | undefined
    type?: ErrorType | string
}

export interface LoginResponse {
    error?: string
    role?: string
    type?: ErrorType
    isFirstLogin?: boolean
}

export interface Session {
    user: User
    accessToken: string
    refreshToken: string
    exp: number
    credit?: number
}

export interface ITokens {
    accessToken: string,
    refreshToken: string
}

export interface ITokenClaims {
    email: string
    name: string
    role: Role
    exp: number
    iat: number
    credits: number
    profile_picture: string
    user_id: string //TODO: Remove this make the user_id (id)
}
