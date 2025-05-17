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

export interface Lecture {
    id: string
    title: string
    description: string
    video: File | null
    attachments: File[] | null
    chapter: string
}

export interface Chapter {
    readonly id: string
    title: string
    // lectures?: string[]
    lectures: Lecture[]
    course: string
}

export type CreateChapter = Omit<Chapter, 'id' | "lectures">;
export type CreateLecture = Omit<Lecture, 'id'>;

