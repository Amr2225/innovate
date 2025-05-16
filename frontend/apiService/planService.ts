import axios from "axios";
import { Plan } from "@/types/institution.type";

export const getPlans = async (): Promise<Plan[]> => {
    try {
        const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/institution/plans/`);
        return res.data;
    } catch {
        return [];
    }
};

export const getPlanDetails = async (planId: string): Promise<Plan> => {
    const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/institution/plans/${planId}/`);
    return res.data;
};