import { api } from "@/apiService/api"
import { Chapter, Course, Lecture, CreateChapter, CreateLecture } from "@/types/course.type"

interface GetCoursesResponse {
    data: Course[]
    message?: string
}

export const getCourses = async (): Promise<Course[]> => {
    const res = await api.get<GetCoursesResponse>("/courses/", { params: { page_size: 10000 } })

    if (res.status === 200) return res.data.data
    throw new Error(res.data.message || "Failed to get courses")
}

export const createCourse = async (course: Course): Promise<Course> => {
    const res = await api.post<Course>("/courses/", course)

    if (res.status === 201) return res.data
    throw new Error("Failed to create course")
}

export const createChapterService = async (chapter: CreateChapter): Promise<Chapter> => {
    const res = await api.post<Chapter>("/chapter/", chapter)

    if (res.status === 201) return res.data
    throw new Error("Failed to create chapter")
}


export const CreateLectureService = async (lecture: CreateLecture): Promise<Lecture> => {
    const res = await api.post<Lecture>("/lecture/", lecture)

    if (res.status === 201) return res.data
    throw new Error("Failed to create lecture")
}


