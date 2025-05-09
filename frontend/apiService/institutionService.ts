import { api } from "@/apiService/api";
import { transformData } from "@/lib/transformations";
import { InstitutionMembersType, SubmissionData } from "@/types/user.types";
import { getSession } from "@/lib/session";


interface GetMembersResponse {
    data: InstitutionMembersType[]
    next: number | null
    previous: number | null
    page_size: number
    total_pages: number
    total_items: number
}

export const getMembers = async (pageParam: number, pageSize: number): Promise<GetMembersResponse> => {
    const res = await api.get("/institution/users/", { params: { page: pageParam, page_size: pageSize } })

    if (res.status === 200) return res.data
    throw new Error(res.data.message || "Failed to get users")
}

export const bulkUserInsert = async (formData: FormData): Promise<SubmissionData[]> => {
    const res = await api.post("/institution/users/register/csv/", formData, {
        headers: {
            'Content-Type': "multipart/form-data"
        }
    });
    const session = await getSession();
    if (!session) {
        throw new Error("Session not found");
    }
    return transformData(res.data, session.user.name);
};