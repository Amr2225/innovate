import { auth } from "@/auth"
import {
    DEFAULT_LOGIN_REDIRECT,
    authRoutes,
    apiAuthPrefix,
    teacherRoutes,
    studentRoutes,
    institutionRoutes,
    TEACHER_ROUTE,
    STUDENT_ROUTE,
    INSTITUTION_ROUTE,
    FIRST_LOGIN_ROUTE,
    LOGIN_ROUTE,
    firstLoginRoutes
} from "@/routes"
import { NextResponse } from "next/server"


export default auth(async (req) => {
    const { nextUrl, auth } = req
    // console.log(req);
    // console.log(auth);

    // console.log("origin", originRequestURL);
    // console.log("AUTH", auth);
    // console.log("PATH NAME", nextUrl.pathname);

    // User Specific
    const isLoggedIn = !!auth // Will contain the user session if authenticated {user: {}, expires: Date} !! to turn it into a boolean

    //Role
    const isInstitution = auth?.user.role === "Institution"
    const isTeacher = auth?.user.role === "Teacher"
    const isStudent = auth?.user.role === "Student"
    const isFirstLogin = !!auth && !auth?.user?.email

    // Routes Specific
    const isAPIAuthRoute = nextUrl.pathname.startsWith(apiAuthPrefix)
    const isAuthRoute = authRoutes.includes(nextUrl.pathname)

    const isTeacherRoute = teacherRoutes.includes(nextUrl.pathname)
    const isStudentRoute = studentRoutes.includes(nextUrl.pathname)
    const isInstitutionRoute = institutionRoutes.includes(nextUrl.pathname)

    const isFirstLoginRoute = firstLoginRoutes.includes(nextUrl.pathname)

    const isProtectedRoute = isTeacherRoute || isStudentRoute || isInstitutionRoute || isFirstLoginRoute

    // console.log(isAPIAuthRoute, isPublicRoute, isAuthRoute, isLoggedIn);

    if (isAPIAuthRoute) return; //For auth js routes

    if (isTeacherRoute && !isTeacher) return NextResponse.redirect(new URL(LOGIN_ROUTE, nextUrl))
    if (isStudentRoute && !isStudent) return Response.redirect(new URL(LOGIN_ROUTE, nextUrl))
    if (isInstitutionRoute && !isInstitution) return Response.redirect(new URL(LOGIN_ROUTE, nextUrl))

    if (isFirstLoginRoute && !isFirstLogin) return Response.redirect(new URL(LOGIN_ROUTE, nextUrl))


    if (isProtectedRoute && !isLoggedIn) return Response.redirect(new URL("/", nextUrl))

    if (isLoggedIn) {
        if (isAuthRoute) {
            if (isStudent) return Response.redirect(new URL(STUDENT_ROUTE, nextUrl))
            if (isTeacher) return Response.redirect(new URL(TEACHER_ROUTE, nextUrl))
            if (isInstitution) return Response.redirect(new URL(INSTITUTION_ROUTE, nextUrl))
            if (isFirstLogin) return Response.redirect(new URL(FIRST_LOGIN_ROUTE, nextUrl))
        }

        if (isFirstLogin && !isFirstLoginRoute) return NextResponse.redirect(new URL(FIRST_LOGIN_ROUTE, nextUrl))

        if (isAuthRoute && !isFirstLogin) return NextResponse.redirect(new URL(DEFAULT_LOGIN_REDIRECT, nextUrl))

        return;
    }

    return;
})


export const config = {
    matcher: [
        // Skip Next.js internals and all static files, unless found in search params
        '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
        // Always run for API routes
        '/(api|trpc)(.*)',
    ],
}