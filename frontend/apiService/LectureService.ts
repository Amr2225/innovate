import { Lecture } from "@/types/course.type"
import { api } from "./api"

export const getLectures = async ({ chpaterId, page_size, pageParam, courseId }: { chpaterId?: string, page_size?: number, pageParam?: number, courseId?: string }): Promise<Lecture[]> => {
    const res = await api.get<{ data: Lecture[] }>("/lecture/", { params: { chapter: chpaterId, chapter__course: courseId, page_size, page: pageParam } })

    if (res.status === 200) return res.data.data
    throw new Error("Failed to get lectures")
}


export const changeLectureProgress = async ({ lectureId, completed, time_spent }: { lectureId: string, completed: boolean, time_spent: number }): Promise<Lecture> => {
    const res = await api.post<{ data: Lecture }>("/lecture/progress", { lecture: lectureId, completed, time_spent })

    if (res.status === 200) return res.data.data
    throw new Error("Failed to change lecture progress")
}


