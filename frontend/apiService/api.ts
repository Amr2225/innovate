import axios from "axios";
import { getSession, setSession, logout } from "@/lib/session";
import moment from "moment";

export const BASE_URL = process.env.NEXT_PUBLIC_API_URL
export const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': "application/json"
    },
    validateStatus: status => status < 500
})


const refreshToken = async () => {
    try {
        const session = await getSession();
        if (!session || session?.refreshToken) throw new Error("No refresh token");

        const response = await axios.post(`${BASE_URL}/auth/token/refresh/`, {
            refresh: session.refreshToken,
        });

        await setSession("innovate-auth", {
            accessToken: response.data.access,
            refreshToken: session.refreshToken
        });


        return response.data.access;
    } catch {
        await logout();
        throw new Error("Failed to refresh token");
        // redirect("/login");
    }
};

api.interceptors.request.use(
    async (config) => {
        let session = await getSession();
        if (!session) {
            await logout();
            throw new Error("Failed to get session");
        }

        // Refresh token if expired
        if (session?.exp && moment.unix(session.exp).isBefore(moment())) {
            await refreshToken();
            session = await getSession();
        }

        if (session) {
            if (session.accessToken) config.headers.Authorization = `Bearer ${session.accessToken}`
        }

        return config
    },
    (error) => Promise.reject(error)

)