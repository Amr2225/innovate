import axios from "axios";
import { getSession, setSession, logout } from "./session";
import { redirect } from "next/navigation";
import moment from "moment";

export const BASE_URL = process.env.NEXT_PUBLIC_API_URL
export const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': "application/json"
    },
    validateStatus: status => status < 500
})

export const apiUserImport = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': "multipart/form-data"
    },
    validateStatus: status => status < 500
})

const refreshToken = async () => {
    try {
        const session = await getSession();
        if (!session?.refreshToken) throw new Error("No refresh token");

        const response = await api.post("/auth/token/refresh/", {
            refresh: session.refreshToken,
        });

        await setSession("innovate-auth", {
            accessToken: response.data.access,
            refreshToken: session.refreshToken
        });

        return response.data.access;
    } catch {
        await logout();
        redirect("/login");
    }
};

apiUserImport.interceptors.request.use(
    async (config) => {
        let session = await getSession();
        if (!session) {
            await logout();
            redirect("/login");
        }

        // Refresh token if expired
        if (session?.exp && moment.unix(session.exp).isBefore(moment())) {
            await refreshToken();
            session = await getSession();
        }

        if (session?.accessToken) {
            config.headers.Authorization = `Bearer ${session.accessToken}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);


api.interceptors.request.use(
    async (config) => {
        let session = await getSession();
        if (!session) {
            await logout();
            redirect("/login");
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


// let isRefreshing = false;
// let failedRequests: any[] = [];

// api.interceptors.response.use(
//     (response) => response,
//     async (error) => {
//         const originalRequest = error.config;

//         if (error.response.status === 401 && !originalRequest._retry) {
//             console.log("AXIOS 401 ERROR");
//             if (isRefreshing) {
//                 // If a token refresh is already in progress, wait for it to complete
//                 return new Promise((resolve, reject) => {
//                     failedRequests.push({ resolve, reject });
//                 })
//                     .then((token) => {
//                         originalRequest.headers.Authorization = `Bearer ${token}`;
//                         return api(originalRequest);
//                     })
//                     .catch((err) => {
//                         return Promise.reject(err);
//                     });
//             }

//             originalRequest._retry = true;
//             isRefreshing = true;
//             try {
//                 const session = await getSession()
//                 if (!session) throw new Error("no refresh token")

//                 const refreshToken = session.refreshToken
//                 const res = await api.post<{ access: string }>('/auth/token/refresh/', {
//                     refresh: refreshToken
//                 })

//                 originalRequest.headers.Authorization = `Bearer ${res.data.access}`;
//                 // Retry all failed requests with the new token
//                 failedRequests.forEach((prom) => prom.resolve(res.data.access));
//                 failedRequests = [];
//                 return api(originalRequest);


//                 console.log(res);
//                 error.config.headers.Authorization = `Bearer ${res.data.access}`
//                 return axios(error.config)
//             } catch (error) {
//                 // If token refresh fails, reject all failed requests
//                 failedRequests.forEach((prom) => prom.reject(error));
//                 failedRequests = [];
//                 await signOut();
//                 return Promise.reject(error);
//             } finally {
//                 isRefreshing = false
//             }
//         }

//         return Promise.reject(error)
//     }
// )

// api.interceptors.response.use(
//     (response) => response,
//     async (error) => {
//         const config = error?.config;

//         if (error?.response?.status === 401 && !config?.sent) {
//             console.log("AXIOS 401");
//             config.sent = true;

//             const session = await getSession()
//             if (!session) throw new Error("no refresh token")

//             const refreshToken = session.refreshToken
//             const result = await axios.post<{ access: string }>(`${process.env.NEXT_PUBLIC_API_URL}/auth/token/refresh/`, {
//                 refresh: refreshToken
//             })

//             console.log("REFRESH Data", result);

//             if (result?.data.access) {
//                 config.headers = {
//                     ...config.headers,
//                     authorization: `Bearer ${result?.data.access}`,
//                 };
//             }

//             return api(config);
//         }
//         return Promise.reject(error);
//     }
// );

