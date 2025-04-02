export type Role = "Student" | "Teacher" | "Institution";

export interface User {
    id: string
    name: string
    email: string
    role: Role
    credits: number | undefined
}

export interface NewUser {
    national_id: string
}