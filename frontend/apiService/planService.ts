import axios from "axios";
import { Plan } from "@/types/institution.type";
import { api } from "./api";

interface BillingTransaction {
    id: string;
    credits_amount: number;
    order_id: number;
    transaction_id: string;
    payment_status: string;
    valid_from: string;
}
interface PlanDetails {
    id: string
    name: string
    description: {
        isAdvantage: boolean
        text: string
    }[]
    credits: number
    minimum_credits: number
    type: "Silver" | "Gold" | "Diamond"
}

export const getPlans = async (): Promise<Plan[]> => {
    try {
        const res = await axios.get(`${process.env.API_URL}/institution/plans/`, {
            headers: {
                "ngrok-skip-browser-warning": true
            }
        });
        return res.data;
    } catch {
        return [];
    }
};

export const getPlanDetails = async (planId: string): Promise<Plan> => {
    const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/institution/plans/${planId}/`, {
        headers: {
            "ngrok-skip-browser-warning": true
        }
    });
    return res.data;
};


export const getInstitutionCurrentPlan = async (): Promise<PlanDetails> => {
    const res = await api.get(`/institution/current-plan/`);

    if (res.status === 200) return res.data
    throw new Error(res.data.message || "Something went wrong")
};

export const getInstitutionBillingHistory = async (): Promise<BillingTransaction[]> => {
    const response = await api.get<{ data: BillingTransaction[], message?: string }>(`/institution/payment/`, { params: { page: 1, page_size: 1000 } });

    if (response.status === 200) return response.data.data;
    throw new Error(response.data.message || "Failed to get billing history");
};
