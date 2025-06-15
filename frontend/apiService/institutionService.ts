import { api } from "@/apiService/api";
import { transformData } from "@/lib/transformations";
import { InstitutionMembersType, SubmissionData } from "@/types/user.types";
import { getSession } from "@/lib/session";
import axios from "axios";
import { InstitutionRegisterStudentSchemaType } from "@/schema/institutionRegisterSchema";

interface MembersResponse {
    data: InstitutionMembersType[]
    next: number | null
    previous: number | null
    page_size: number
    total_pages: number
    total_items: number
}

interface IGeneratePayment {
    name: string
    email: string
    plan_id: string
    credits: number
    redirection_url?: string
}

interface IMembers {
    pageParam: number
    pageSize: number
    role?: "Teacher" | "Student" | "Institution"
    first_name?: string
    last_name?: string
    email?: string
}

// interface IUpdateUser {
//     first_name?: string
//     middle_name?: string
//     last_name?: string
//     email?: string
//     role?: string
//     national_id?: string
//     birth_date?: string
//     age?: number
// }

// Users Management
export const getMembers = async ({ pageParam, pageSize, role, first_name, last_name, email }: IMembers): Promise<MembersResponse> => {
    const res = await api.get("/institution/users/", { params: { page: pageParam, page_size: pageSize, role, first_name, last_name, email } })

    if (res.status === 200) return res.data
    throw new Error(res.data.message || "Failed to get users")
}

export const updateUser = async ({ userId, data }: { userId: string, data: Record<string, string | number | boolean | Date> }): Promise<SubmissionData[]> => {
    const res = await api.put(`/institution/users/${userId}/`, data)
    if (res.status === 200) return res.data
    throw new Error(res.data.message || "Failed to update user")
}

export const deleteUser = async ({ userId }: { userId: string }): Promise<boolean> => {
    const res = await api.delete(`/institution/users/${userId}/`)
    if (res.status === 204) return true
    throw new Error(res.data.message || "Failed to delete user")
}

export const promoteStudents = async (): Promise<boolean> => {
    const res = await api.post("/enrollments/promote-students/")
    if (res.status === 200) return true
    throw new Error(res.data.message || "Failed to promote students")
}


// Institution User Registration
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
    if (res.status === 200) return transformData(res.data, session.user.name);
    throw new Error(res.data.error || "Failed to add user")
};

export const registerSingleUser = async (data: InstitutionRegisterStudentSchemaType): Promise<boolean> => {
    const res = await api.post("/institution/users/", data)
    if (res.status === 201) return true
    throw new Error(res.data?.detail || "Failed to register user")
}


export const generatePaymentLink = async (data: IGeneratePayment): Promise<string> => {
    const res = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/institution/payment/`, data, {
        headers: {
            // 'Content-Type': 'application/json',
            "ngrok-skip-browser-warning": true
        }
    });
    return res.data.url;
};
