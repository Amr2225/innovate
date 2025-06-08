import { create, StoreApi, UseBoundStore } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { EncryptedStorage } from "./encryptedStorage";

import { Course, Chapter, Lecture } from "@/types/course.type";
import { deleteVideo, saveVideo } from "./videoStorage";
import { convertSecondsToTime } from "@/lib/convertSecondsToTime";
import { deleteAttachmentForLecture, saveAttachment } from "./attachmentStorage";


type CourseStore = {
    course: Course | null;
    chapters: Chapter[];
    addCourse: (course: Course) => void;
    addLecture: (chapterId: string) => void;
    setLecture: (chapterId: string, Lecture: Lecture[]) => void;
    updateLecture: (chapterId: string, lectureId: string, key: keyof Lecture, value: string | File | null) => void;
    deleteLecture: (chapterId: string, lectureId: string) => void;
    addChapter: () => void;
    updateChapter: (chapterId: string, key: string, value: string) => void;
    deleteChapter: (chapterId: string) => void;
    setChapters: (chapters: Chapter[] | ((prev: Chapter[]) => Chapter[])) => void;
    reset: () => void;
}

const initialState: Pick<CourseStore, 'course' | 'chapters'> = {
    course: null,
    chapters: [],
}

const storeCache: Record<string, UseBoundStore<StoreApi<CourseStore>>> = {};

export const createCourseStore = (courseId: string) => {
    if (storeCache[courseId]) return storeCache[courseId];

    const courseStore = create<CourseStore>()(
        persist(
            (set, get) => ({
                ...initialState,
                addCourse: (course: Course) => set({ course }),
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
                                attachments: null,
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
                updateLecture: async (chapterId: string, lectureId: string, key: keyof Lecture, value: string | File | null) => {
                    if (key === "attachments") {
                        if (value instanceof File) {
                            // const storageKey = `attachment_${chapterId}_${lectureId}`;
                            await saveAttachment(value, lectureId);
                            const newChapters = get().chapters?.map((chapter) => chapter.id === chapterId ? {
                                ...chapter,
                                lectures: chapter.lectures.map((lecture) => lecture.id === lectureId ? {
                                    ...lecture,
                                    attachments: {
                                        name: value.name,
                                        type: value.type,
                                        size: value.size,
                                        lastModified: value.lastModified,
                                        file_extension: value.name.split('.').pop() || ''
                                    }
                                } : lecture)
                            } : chapter)

                            set({ chapters: newChapters as Chapter[] });
                        }
                        else if (!value) {
                            deleteAttachmentForLecture(lectureId);
                            const newChapters = get().chapters?.map((chapter) => chapter.id === chapterId ? {
                                ...chapter,
                                lectures: chapter.lectures.map((lecture) => lecture.id === lectureId ? {
                                    ...lecture,
                                    attachments: null
                                } : lecture)
                            } : chapter)

                            set({ chapters: newChapters as Chapter[] });
                        }
                    }
                    else if (key === "video") {
                        if (value instanceof File) {
                            // Create a preview URL for the video
                            const videoPreview = URL.createObjectURL(value);

                            // Create a video element to get the duration
                            const tempVideo = document.createElement("video");
                            tempVideo.src = videoPreview;

                            // To get the video duration 
                            tempVideo.onloadedmetadata = async () => {
                                const duration = Math.round(tempVideo.duration);



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
                                                duration: convertSecondsToTime(duration),
                                                videoPreview: videoPreview,
                                            } : lecture
                                        )
                                    } : chapter
                                );

                                set({ chapters: newChapters as Chapter[] });
                            }
                            tempVideo.remove();
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
                setChapters: (chapters) => set((state) => ({
                    chapters: typeof chapters === 'function' ? chapters(state.chapters) : chapters
                })),
                reset: () => set(initialState),
            }),
            {
                name: `course-store-${courseId}`,
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

    storeCache[courseId] = courseStore;
    return courseStore;
}


