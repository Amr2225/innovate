import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { EncryptedStorage } from "./encryptedStorage";

import { Course, Chapter } from "@/types/course.type";

type CourseStore = {
    course: Course | null;
    chapters: Chapter[];
    addLecture: (chapterId: string) => void;
    updateLecture: (chpaterId: string, lectureId: string, key: string, value: string | File) => void;
    deleteLecture: (chapterId: string, lectureId: string) => void;
    addChapter: () => void;
    updateChapter: (chapterId: string, key: string, value: string) => void;
    reset: () => void;
}

const initialState: Pick<CourseStore, 'course' | 'chapters'> = {
    course: null,
    chapters: [],
}

export const courseStore = create<CourseStore>()(
    persist(
        (set, get) => ({
            ...initialState,
            addLecture: (chapterId: string) => {
                const newChapters = get().chapters?.map((chapter) => chapter.id === chapterId ? {
                    ...chapter,
                    lectures: [
                        ...chapter.lectures,
                        {
                            id: Math.random().toString(),
                            title: "New Lecture",
                            description: "New Lecture Description",
                            video: "",
                            attachments: [],
                        },
                    ]
                } : chapter)

                set({ chapters: newChapters as Chapter[] })
            },
            updateLecture: (chpaterId: string, lectureId: string, key: string, value: string | File) => {
                const newChapters = get().chapters?.map((chapter) => chapter.id === chpaterId ? {
                    ...chapter,
                    lectures: chapter.lectures.map((lecture) => lecture.id === lectureId ? {
                        ...lecture,
                        [key]: value,
                    } : lecture)
                } : chapter)

                set({ chapters: newChapters as Chapter[] })
            },
            deleteLecture: (chapterId: string, lectureId: string) => {
                const newChapters = get().chapters?.map((chapter) => chapter.id === chapterId ? {
                    ...chapter,
                    lectures: chapter.lectures.filter((lecture) => lecture.id !== lectureId)
                } : chapter)

                set({ chapters: newChapters as Chapter[] })
            },
            addChapter: () => set({
                chapters: [
                    ...get().chapters,
                    {
                        id: Math.random().toString(),
                        title: "New Chapter",
                        lectures: [],
                        course: get().course?.id || "",
                    }
                ]
            }),
            updateChapter: (chpaterId: string, key: string, value: string) => {
                const newChapters = get().chapters?.map((chapter) => chapter.id === chpaterId ? {
                    ...chapter,
                    [key]: value,
                } : chapter)

                set({ chapters: newChapters as Chapter[] })
            },
            reset: () => set(initialState),
        }),
        {
            name: "course-store",
            storage: createJSONStorage(() => new EncryptedStorage()),
        }
    )
)



