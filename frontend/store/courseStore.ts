import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { EncryptedStorage } from "./encryptedStorage";

import { Course, Chapter, Lecture } from "@/types/course.type";
import { deleteVideo, saveVideo } from "./videoStorage";

type CourseStore = {
    course: Course | null;
    chapters: Chapter[];
    addLecture: (chapterId: string) => void;
    setLecture: (chapterId: string, Lecture: Lecture[]) => void;
    updateLecture: (chpaterId: string, lectureId: string, key: string, value: string | File | null) => void;
    deleteLecture: (chapterId: string, lectureId: string) => void;
    addChapter: () => void;
    updateChapter: (chapterId: string, key: string, value: string) => void;
    deleteChapter: (chapterId: string) => void;
    setChapters: (chapters: Chapter[]) => void;
    reset: () => void;
}

const initialState: Pick<CourseStore, 'course' | 'chapters'> = {
    course: null,
    chapters: [],
}

export const useCourseStore = create<CourseStore>()(
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
            setLecture: (chapterId: string, Lecture: Lecture[]) => {
                const newChapters = get().chapters?.map((chapter) => chapter.id === chapterId ? {
                    ...chapter,
                    lectures: Lecture
                } : chapter)

                set({ chapters: newChapters as Chapter[] })
            },
            updateLecture: async (chapterId: string, lectureId: string, key: string, value: string | File | null) => {
                if (key === "video") {
                    if (value instanceof File) {
                        // Create a preview URL for the video
                        const videoPreview = URL.createObjectURL(value);

                        // Store the file in IndexedDB
                        const storageKey = `video_${chapterId}_${lectureId}`;
                        await saveVideo(storageKey, value);

                        const newChapters = get().chapters?.map((chapter) =>
                            chapter.id === chapterId ? {
                                ...chapter,
                                lectures: chapter.lectures.map((lecture) =>
                                    lecture.id === lectureId ? {
                                        ...lecture,
                                        video: {
                                            name: value.name,
                                            type: value.type,
                                            size: value.size,
                                            lastModified: value.lastModified,
                                            storageKey: storageKey
                                        },
                                        videoPreview: videoPreview
                                    } : lecture
                                )
                            } : chapter
                        );

                        set({ chapters: newChapters as Chapter[] });
                    }
                    // Delete the video from state and IndexedDB
                    else if (!value) {
                        const storageKey = `video_${chapterId}_${lectureId}`;
                        const newChapters = get().chapters?.map((chapter) => chapter.id === chapterId ? {
                            ...chapter,
                            lectures: chapter.lectures.map((lecture) => lecture.id === lectureId ? {
                                ...lecture,
                                video: null
                            } : lecture)
                        } : chapter)

                        deleteVideo(storageKey);
                        set({ chapters: newChapters as Chapter[] });
                    }
                } else {
                    const newChapters = get().chapters?.map((chapter) => chapter.id === chapterId ? {
                        ...chapter,
                        lectures: chapter.lectures.map((lecture) => lecture.id === lectureId ? {
                            ...lecture,
                            [key]: value,
                        } : lecture)
                    } : chapter)

                    set({ chapters: newChapters as Chapter[] })
                }
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
            deleteChapter: (chapterId: string) => {
                const newChapters = get().chapters?.filter((chapter) => chapter.id !== chapterId)
                set({ chapters: newChapters as Chapter[] })
            },
            setChapters: (chapters: Chapter[]) => set({ chapters }),
            reset: () => set(initialState),
        }),
        {
            name: "course-store",
            storage: createJSONStorage(() => new EncryptedStorage()),
            partialize: (state) => ({
                ...state,
                chapters: state.chapters.map(chapter => ({
                    ...chapter,
                    lectures: chapter.lectures.map(lecture => ({
                        ...lecture,
                        video: lecture.video ? {
                            name: lecture.video.name,
                            type: lecture.video.type,
                            size: lecture.video.size,
                            lastModified: lecture.video.lastModified,
                            storageKey: lecture.video.storageKey
                        } : null,
                        videoPreview: lecture.videoPreview
                    }))
                }))
            })
        }
    )
)

