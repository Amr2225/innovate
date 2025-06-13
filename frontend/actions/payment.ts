'use server'
import { api } from "@/apiService/api"


// interface IGeneratePayment {
//     name: string
//     email: string
//     plan_id: string
//     credits: number
// }

interface IBuyCreditsResponse {
    isSuccess: boolean
    message?: string
}

export const buyCredits = async (hmac: string): Promise<IBuyCreditsResponse> => {
    const res = await api.post('/institution/buy-credits/', { hmac })
    if (res.status == 201) return { isSuccess: true }
    console.log(res.data);
    return { isSuccess: false, message: res.data.message || "Failed to buy credits, please try again" }
}

// export const generatePaymentLink = async (data: IGeneratePayment): Promise<IBuyCreditsResponse & { url?: string }> => {
//     const res = await api.post('/institution/payment/', data)
//     if (res.status == 200) return { isSuccess: true, url: res.data.url }
//     return { isSuccess: false, message: res.data.message || "Failed to generate payment link, please try again" }
// }

