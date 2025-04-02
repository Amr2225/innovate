import NextAuth, { AuthError } from "next-auth"
import authConfig from "@/auth.config"
import jwt from "jsonwebtoken"

// Types
import { JWT } from "next-auth/jwt"
import { Role, User as IUser } from "@/types/user.types"
// import { CredentialsError, EmailVerificationError } from "@/errors/auth.error"

declare module "next-auth" {
    interface Session {
        accessToken: string
        refreshToken: string
        user: IUser
        expiryTime: number
    }

    interface User {
        access: string
        refresh: string
        error: string | undefined
    }
}

declare module "next-auth/jwt" {
    interface JWT {
        role?: Role
        access: string
        refresh: string
        user_id: string
        full_name: string
        expiryTime: number
    }

    // interface user {
    //     access: string
    // }
}

// class CredentialsError extends CredentialsSignin {
//     code = "Invalid email or password"
// }
// class CredentialsError extends E {
//     code = "Invalid email or password"
// }

const ACCESS_TOKEN_EXPIRY_TIME_MINUTES = +process.env.ACCESS_TOKEN_EXPIRY_TIME_MINUTE!

export const { handlers, signIn, signOut, auth } = NextAuth({
    ...authConfig,
    session: {
        strategy: "jwt",
        maxAge: ACCESS_TOKEN_EXPIRY_TIME_MINUTES * 60,
    },
    pages: {
        signIn: "/login",
        signOut: "/auth/signout",
        error: "/auth/error",
        verifyRequest: "/auth/verify-request",
        newUser: "/auth/new-user",
    },
    events: {
        signIn: async (user) => {
            console.log("@EVENTS", user);
            // if (!user.user.refresh)
            //     redirect('/register')
            // redirect("/dashboard")
        },
    },
    callbacks: {
        async signIn({ account, user }) {
            if (account?.provider === "google") console.log('Google Sign In', account, user);

            console.log("USER", user);
            if (user.error) {
                throw new Error(user.error)
                // if (user.error_code === 401 || user.error_code === 400) throw new CredentialsError();
                // if (user.error_code === 403) throw new EmailVerificationError();
                // thow new AuthError("Something went wrong");
            }

            return true
        },
        async jwt({ token, user, trigger, session }) {
            if (trigger === "update" && session?.accessToken) {
                console.log("Update Session", session);
                const decodedToken = jwt.decode(session.accessToken) as JWT
                token = { ...decodedToken as JWT, access: session.accessToken, refresh: token.refresh, expiryTime: decodedToken.exp! }
                return token
            }

            if (user) {
                const decodedToken = jwt.decode(user.access) as JWT
                token = { ...decodedToken as JWT, access: user.access, refresh: user.refresh, expiryTime: decodedToken.exp! }
            }
            return token
        },
        async session({ session, token }) {
            session.accessToken = token.access
            session.refreshToken = token.refresh
            session.user.id = token.user_id
            session.user.name = token.full_name || token.name!
            session.user.role = token.role!
            session.expiryTime = token.expiryTime

            return session
        }
    },
})