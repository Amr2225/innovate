import axios from "axios";
import { useSession, signOut } from "next-auth/react";
import api, { BASE_URL } from "@/apiService/api";
import { useEffect } from "react";
import moment from "moment";


const getNewAccessToken = async (refreshToken: string): Promise<string | undefined> => {
    try {
        const res = await axios.post<{ access: string }>(`${BASE_URL}/auth/token/refresh/`, { refresh: refreshToken })
        return res.data.access
    } catch (e) {
        console.log("SINGED OUT");
        await signOut()
    }
}

const useApi = () => {
    const { data: session, update } = useSession();

    useEffect(() => {
        const requestInterceptor = api.interceptors.request.use(
            async (config) => {
                if (session) {
                    if (session.accessToken) config.headers.Authorization = `Bearer ${session.accessToken}`

                    const isExpired = moment.unix(session.expiryTime).diff(moment()) < 1
                    if (!isExpired) return config
                    console.log("TOKEN EXPIRED....");


                    const newAccessToken = await getNewAccessToken(session.refreshToken)
                    update({ accessToken: newAccessToken })
                    config.headers.Authorization = `Bearer ${newAccessToken}`
                }

                return config
            },
            (error) => Promise.reject(error)
        )

        return () => api.interceptors.request.eject(requestInterceptor)

    }, [session])

    return api
}

export default useApi