import { InstitutionPolicy } from "@/types/institution.type";
import { api } from "./api";

export const getInstitutionPolicy = async () => {

    const response = await api.get<InstitutionPolicy>('policy/');
    if (response.status === 200) return response.data;
    throw new Error("Something went wrong");
}

export const updateInstitutionPolicy = async (policy: InstitutionPolicy) => {
    const response = await api.put<InstitutionPolicy>('policy/', policy);
    if (response.status === 200) return true;
    throw new Error("Something went wrong");
}




