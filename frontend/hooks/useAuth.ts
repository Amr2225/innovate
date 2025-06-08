import { getSession } from "@/lib/session";
import { User } from "@/types/user.types";
import { useCallback, useEffect, useState } from "react"
import { refreshToken as updateToken } from "@/apiService/api";


export function useAuth() {
    const [accessToken, setAccessToken] = useState<string | null>(null);
    const [refreshToken, setRefreshToken] = useState<string | null>(null);
    const [user, setUser] = useState<User | null>(null);
    const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);

    const getToken = async () => {
        const session = await getSession()
        if (session) {
            setAccessToken(session.accessToken)
            setRefreshToken(session.refreshToken)
            setUser({ name: session.user.name, email: session.user.email, role: session.user.role })
            setIsLoggedIn(true)
        }
    }

    useEffect(() => {
        getToken()
    }, [])


    const updateUser = useCallback(async () => {
        await updateToken();
    }, [])

    return {
        user,
        accessToken,
        refreshToken,
        isLoggedIn,
        updateUser
    }

}