import axios from "axios";
import { Plan } from "@/types/institution.type";
import { api } from "./api";

interface PlanDetails {
    id: string
    name: string
    description: string
    credits: number
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