import { api } from "@/lib/api";
import { InstitutionMembersType } from "@/types/user.types";

export const getMembers = async (): Promise<InstitutionMembersType[]> => {
    const res = await api.get("/auth/institution/users/")

    if (res.status === 200) return res.data

    throw new Error(res.data.message || "Failed to get users")

}