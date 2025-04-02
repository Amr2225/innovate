export interface ILogin {
    refresh: string;
    access: string;
}

export type ErrorType = "CredentialsSignin" | "Verification" | "RegistrationError" | "CredentialError"
export interface LoginError {
    message: string | undefined
    type?: ErrorType
}

export interface LoginErrorProps {
    error: LoginError
}