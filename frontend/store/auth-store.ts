// import { create } from "zustand";
// import { persist, createJSONStorage, StateStorage } from "zustand/middleware";
// import { User } from "next-auth";
// import { ILogin } from "@/types/auth.type";
// import cookies from "js-cookie";
// import axios from "axios";

// const cookieStorage: StateStorage = {
//     getItem: (name: string) => {
//         if (typeof window === 'undefined') return null
//         return cookies.get(name) || null
//     },
//     setItem: (name: string, value: string) => {
//         cookies.set(name, value, {
//             expires: 7, // 7 days
//             secure: true,
//             sameSite: 'strict'
//         });
//     },
//     removeItem: (name: string) => cookies.remove(name),
// };

// interface AuthState {
//     user: User | null;
//     refreshToken: string | null;
//     token: string | null;
//     login: (email: string, password: string) => Promise<void>;
//     getToken: () => string | null;
//     setToken: (token: string) => void;
//     clearToken: () => void;
// }

// const useAuthStore = create<AuthState>()(
//     persist(
//         (set, get) => ({
//             token: null,
//             refreshToken: null,
//             user: null,
//             loading: false,
//             error: null,

//             login: async (email: string, password: string) => {
//                 const res = await axios.post<ILogin>(`${process.env.NEXT_PUBLIC_API_URL}/auth/login/`, { email, password })
//                 set({ token: res.data.access });
//             },

//             setToken: (token: string) => {
//                 set({ token });
//             },

//             getToken: () => {
//                 return get().token;
//             },

//             clearToken: () => {
//                 set({ token: null });
//             }
//         }),
//         {
//             name: "innovate-auth",
//             // storage: createJSONStorage(() => cookieStorage),
//             partialize: (state) => ({
//                 token: state.token,
//                 refreshToken: state.refreshToken,
//                 user: state.user
//             })
//             // partialize: (state) => {
//             //     // Get the current cookie value
//             //     const cookieValue = cookies.get("innovat-auth");
//             //     if (cookieValue) {
//             //         try {
//             //             const parsed = JSON.parse(cookieValue);
//             //             return {
//             //                 token: parsed.state?.token || state.token,
//             //                 refreshToken: parsed.state?.refreshToken || state.refreshToken,
//             //                 user: parsed.state?.user || state.user,
//             //             };
//             //         } catch (e) {
//             //             console.error("Error parsing cookie:", e);
//             //         }
//             //     }
//             //     return {
//             //         token: state.token,
//             //         refreshToken: state.refreshToken,
//             //         user: state.user,
//             //     };
//             // },
//         }
//     )
// )

// export default useAuthStore;




