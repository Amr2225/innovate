import { api, apiUserImport } from "@/lib/api";
import { transformData } from "@/lib/transformations";
import { InstitutionMembersType, SubmissionData } from "@/types/user.types";
import { getSession } from "@/lib/session";

export const getMembers = async (): Promise<InstitutionMembersType[]> => {
    const res = await api.get("/auth/institution/users/")

    if (res.status === 200) return res.data
    throw new Error(res.data.message || "Failed to get users")
}

export const bulkUserInsert = async (formData: FormData): Promise<SubmissionData[]> => {
    const res = await apiUserImport.post("/auth/institution/users/register/csv/", formData);
    const session = await getSession();
    if (!session) {
        throw new Error("Session not found");
    }
    return transformData(res.data, session.user.name);
};