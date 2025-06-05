import { api } from "./api"

interface EligibleCourses {
    id: string
    name: string
    description: string
    instructors: Instructor[]
    credit_hours: number
}

interface Instructor {
    id: string
    full_name: string
    avatar: string
}


export const getEligibleCourses = async (): Promise<EligibleCourses[]> => {
    const res = await api.get<EligibleCourses[]>("/enrollments/")

    if (res.status === 200) return res.data
    throw new Error("Failed to get eligible courses")
}

export const enrollInCourse = async (courseId: string) => {
    const res = await api.post("/enrollments/", { courses: [courseId] })
    if (res.status === 201) return true
    throw new Error(res.data.error || "Failed to enroll")
}


