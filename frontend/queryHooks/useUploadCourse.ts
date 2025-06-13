import { createChapterService, createCourse } from "@/apiService/courseService";
import { getAttachmentForLecture } from "@/store/attachmentStorage";
import { createCourseStore, deleteCourseStore } from "@/store/courseStore";
import { getVideo } from "@/store/videoStorage";
import { Chapter } from "@/types/course.type";
import { useMutation } from "@tanstack/react-query";
import { useMemo } from "react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

export function useUploadCourse(courseId: string) {
    const router = useRouter();

    const useCourseStore = createCourseStore(courseId);
    const { course, chapters } = useCourseStore();

    const { mutate: createCourseMutation, isPending: isCreatingCourse } = useMutation({
        mutationFn: () => createCourse(course!),
        onSuccess: (data) => {
            createChapter(createFormData(chapters!, data.id));
        },
        onError: (e) => {
            toast.error(e.message || "Failed to create course");
        },
    })


    const { mutate: createChapter, isPending: isCreatingChapter } = useMutation({
        mutationFn: (chapterData: FormData) => createChapterService(chapterData),
        onSuccess: () => {
            toast.success("Course created successfully");
            deleteCourseStore(courseId);
            router.push(`/institution/courses`);
        },
        onError: (error) => {
            console.log(error);
        },
    });

    const createFormData = (chapters: Chapter[], courseId: string) => {
        const ChapterDataWithCourseId = chapters.map((chapter) => ({
            ...chapter,
            courseId: courseId
        }));

        const formData = new FormData();
        formData.append("chapters", JSON.stringify(ChapterDataWithCourseId));
        ChapterDataWithCourseId.forEach((chapter, chapterIndex) => {
            chapter.lectures.forEach(async (lecture, lectureIndex) => {
                // formData.append(`lectures[${index}][title]`, lecture.title);
                if (lecture.video) {
                    const video = await getVideo(lecture.video?.storageKey as string);
                    formData.append(`chapter_${chapterIndex}_lecture_${lectureIndex}_video`, video as File);
                }

                if (lecture.attachments) {
                    const attachment = await getAttachmentForLecture(lecture.id);
                    formData.append(`chapter_${chapterIndex}_lecture_${lectureIndex}_attachment`, attachment as File);
                }
            })
        })
        return formData;
    }

    const isCreating = useMemo(() => {
        return isCreatingCourse || isCreatingChapter;
    }, [isCreatingCourse, isCreatingChapter]);


    const UploadCourse = () => {
        createCourseMutation();
    }

    return {
        UploadCourse,
        isCreating
    }
}