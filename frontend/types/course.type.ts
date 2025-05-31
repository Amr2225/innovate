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

