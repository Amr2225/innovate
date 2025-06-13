import { NextRequest, NextResponse } from "next/server"
import { getSession } from "./lib/session"
import {
    DEFAULT_LOGIN_REDIRECT,
    authRoutes,
    TEACHER_ROUTE,
    STUDENT_ROUTE,
    INSTITUTION_ROUTE,
    FIRST_LOGIN_ROUTE,
    LOGIN_ROUTE,
    firstLoginRoutes
} from "@/routes"


export default async function middleware(req: NextRequest) {
    const { nextUrl } = req
    const headers = new Headers(req.headers);
    headers.set("x-current-path", req.nextUrl.pathname);
    const session = await getSession()


    const isLoggedIn = !!session
    const user = session?.user

    const isTeacher = user?.role === "Teacher"
    const isStudent = user?.role === "Student"
    const isInstitution = user?.role === "Institution"
    const isFirstLogin = !!user && !user?.email

    // Routes Specific
    const isAuthRoute = authRoutes.some((route) => nextUrl.pathname.startsWith(route))

    // const isTeacherRoute = teacherRoutes.includes(nextUrl.pathname)
    // const isStudentRoute = studentRoutes.includes(nextUrl.pathname)
    // const isInstitutionRoute = institutionRoutes.includes(nextUrl.pathname)

    const isTeacherRoute = nextUrl.pathname.startsWith('/teacher')
    const isStudentRoute = nextUrl.pathname.startsWith('/student')
    const isInstitutionRoute = nextUrl.pathname.startsWith('/institution')

    const isFirstLoginRoute = firstLoginRoutes.includes(nextUrl.pathname)

    const isProtectedRoute = isTeacherRoute || isStudentRoute || isInstitutionRoute || isFirstLoginRoute

    console.log(isAuthRoute, isLoggedIn);


    if (isTeacherRoute && !isTeacher) return NextResponse.redirect(new URL(LOGIN_ROUTE, nextUrl.origin))
    if (isStudentRoute && !isStudent) return NextResponse.redirect(new URL(LOGIN_ROUTE, nextUrl.origin))
    if (isInstitutionRoute && !isInstitution) return NextResponse.redirect(new URL(LOGIN_ROUTE, nextUrl.origin))

    if (isFirstLoginRoute && !isFirstLogin) return NextResponse.redirect(new URL(LOGIN_ROUTE, nextUrl.origin))

    if (isProtectedRoute && !isLoggedIn) return NextResponse.redirect(new URL("/", nextUrl.origin))

    if (isLoggedIn) {
        if (isAuthRoute) {
            if (isStudent) return NextResponse.redirect(new URL(STUDENT_ROUTE, nextUrl.origin))
            if (isTeacher) return NextResponse.redirect(new URL(TEACHER_ROUTE, nextUrl.origin))
            if (isInstitution) return NextResponse.redirect(new URL(INSTITUTION_ROUTE, nextUrl.origin))
            if (isFirstLogin) return NextResponse.redirect(new URL(FIRST_LOGIN_ROUTE, nextUrl.origin))
        }

        if (isFirstLogin && !isFirstLoginRoute) return NextResponse.redirect(new URL(FIRST_LOGIN_ROUTE, nextUrl.origin))

        if (isAuthRoute && !isFirstLogin) return NextResponse.redirect(new URL(DEFAULT_LOGIN_REDIRECT, nextUrl.origin))

        return;
    }

    return;
}


export const config = {
    matcher: [
        // Skip Next.js internals and all static files, unless found in search params
        '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
        // Always run for API routes
        '/(api|trpc)(.*)',
    ],
}