// import { FileData } from "./file.type"

export interface Course {
    id: string
    name: string
    description: string
    prerequisite_course: string | null
    credit_hours: number
    total_grade: number
    semester: number
    instructors: string[]
    instructors_detials?: {
        id: string
        full_name: string
        email: string
        avatar: string | null
    }[]
    prerequisite_course_detail?: {
        id: string
        name: string
        description: string
    }
}

// export interface InstructorCourseType extends Course {
//     prerequisite_course: number | null
// }

export interface Lecture {
    readonly id: string
    title: string
    description: string
    video: {
        name: string
        type: string
        size: number
        lastModified: number
        storageKey: string
    } | null
    duration: string
    videoPreview: string | null
    attachments: {
        name: string
        type: string
        size: number
        lastModified: number
        file_extension: string
    } | null
    chapter: string
}

export interface LectureResponse {
    readonly id: string
    title: string
    description: string
    video: string
    attachments: string
    updatedAt: string
}

export interface ChapterResponse {
    readonly id: string
    lectures: LectureResponse[]
    course: string
    title: string
}

export interface Chapter {
    id: string
    title: string
    // lectures?: string[]
    lectures: Lecture[]
    course: string
}

export interface CreateChapter {
    title: string
    courseId: string
    lectures: Omit<Lecture, 'id'>[]
    credit_hours: number
    total_grade: number
}


// export type CreateChapter = Omit<Chapter, 'id' | "lectures">;
export type CreateLecture = Omit<Lecture, 'id'>;

