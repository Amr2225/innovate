import { api } from "./api"

interface EligibleCourses {
    id: string
    name: string
    description: string
    instructors: Instructor[]
    credit_hours?: number
}

interface Instructor {
    id: string
    full_name: string
    avatar: string
}

interface StudentCourses {
    id: string
    name: string
    description: string
    instructors_details: {
        id: string
        full_name: string
        email: string
    }[]
    credit_hours: number
}


export const getEligibleCourses = async (): Promise<EligibleCourses[]> => {
    const res = await api.get<{ data: EligibleCourses[], detail: string }>("/enrollments/", { params: { page_size: 100, page_number: 1 } })

    if (res.status === 200) return res.data.data
    throw new Error(res.data.detail || "Failed to get eligible courses")
}

export const enrollInCourse = async (courseId: string) => {
    const res = await api.post("/enrollments/", { courses: [courseId] })
    if (res.status === 201) return true
    throw new Error(res.data.error || "Failed to enroll")
}


export const getStudentCourses = async ({ page_size, pageParam }: { page_size: number, pageParam: number }): Promise<StudentCourses[]> => {
    const res = await api.get<{ data: StudentCourses[] }>("/enrollments/my-courses/", { params: { page_size, pageParam } })

    if (res.status === 200) return res.data.data
    throw new Error("Failed to get student courses")
}

