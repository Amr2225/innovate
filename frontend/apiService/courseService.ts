import { api } from "@/apiService/api"
import { Chapter, Course, Lecture, CreateLecture } from "@/types/course.type"

interface GetCoursesResponse<T> {
    data: T[]
    message?: string
    previous: number | null
    next: number | null
    page: number
    page_size: number
    total_pages: number
    total_items: number,
}

// interface ErrorrResponseType {
//     message?: string
// }

// Get all courses for institution and student and teacher each based on their roles
export const getCourses = async <T = Course>({ page_size, pageParam }: { page_size?: number, pageParam?: number }): Promise<GetCoursesResponse<T>> => {
    const res = await api.get<GetCoursesResponse<T>>("/courses/", {
        params: { page_size, page: pageParam },
    });

    // console.log(res);

    if (res.status === 200) return res.data
    throw new Error(res.data.message || "Failed to get courses")
}

export const createCourse = async (course: Course): Promise<Course> => {
    const res = await api.post<Course>("/courses/", course)

    if (res.status === 201) return res.data
    throw new Error(res.data.name[0] || "Failed to create course")
}

export const createChapterService = async (chapterData: FormData): Promise<Chapter[]> => {
    const res = await api.post<{ chpaters: Chapter[] }>("/chapter/", chapterData, {
        headers: {
            "Content-Type": "multipart/form-data"
        }
    })

    if (res.status === 201) return res.data.chpaters
    throw new Error("Failed to create chapter")
}

export const CreateLectureService = async (lecture: CreateLecture): Promise<Lecture[]> => {
    const res = await api.post<{ lectures: Lecture[] }>("/lecture/", lecture)

    if (res.status === 201) return res.data.lectures
    throw new Error("Failed to create lecture")
}

// -------------------------------------------
// ----------Teacher Courses Services----------
// -------------------------------------------

// export const getTeacherCourses = async (): Promise<Course[]> => {
//     const res = await api.get<GetCoursesResponse<Course>>("/courses/teacher/")

//     if (res.status === 200) return res.data.data
//     throw new Error(res.data.message || "Failed to get courses")
// }


