// Any user can access 
export const publicRoutes = [
    '/',
    '/contact',
    '/about',
    '/dashboard'
]

// if logged in cannot access these routes
export const authRoutes = [
    '/login',
    '/login-access',
    '/register-institution',
]

// Only Authenticated users
export const protectedRoutes = [
    '/dashboard'
]

export const teacherRoutes = [
    '/teacher/dashboard'
]

export const studentRoutes = [
    '/student/dashboard'
]

export const institutionRoutes = [
    '/institution/dashboard'
]

export const firstLoginRoutes = [
    '/register-user'
]

export const apiAuthPrefix = '/api/auth'
export const DEFAULT_LOGIN_REDIRECT = '/dashboard'

//Constants and intial route URLs
export const LOGIN_ROUTE = '/login'
export const STUDENT_ROUTE = '/student/dashboard'
export const TEACHER_ROUTE = '/teacher/dashboard'
export const INSTITUTION_ROUTE = '/institution/dashboard'
export const FIRST_LOGIN_ROUTE = '/register-user'