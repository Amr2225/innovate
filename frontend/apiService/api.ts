import axios from "axios";
import { getSession, setSession, logout } from "@/lib/session";
import moment from "moment";
import { toast } from "sonner";

export const BASE_URL = process.env.NEXT_PUBLIC_API_URL
export const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': "application/json",
        "ngrok-skip-browser-warning": true
    },
    validateStatus: status => status < 500
})


export const refreshToken = async () => {
    try {
        const session = await getSession();
        if (!session?.refreshToken) throw new Error("No refresh token");

        const response = await axios.post(`${BASE_URL}/auth/token/refresh/`, {
            refresh: session.refreshToken,
        }, {
            headers: {
                'Content-Type': 'application/json',
                "ngrok-skip-browser-warning": "on"
            }
        });

        await setSession("innovate-auth", {
            accessToken: response.data.access,
            refreshToken: session.refreshToken
        });
    } catch (e) {
        console.log(e);
        await logout();
        toast.error("Session expired, please login again");
        throw new Error("Failed to refresh token");
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