import { createChapterService } from "@/apiService/courseService";
import { getAttachmentForLecture } from "@/store/attachmentStorage";
import { createCourseStore, deleteCourseStore } from "@/store/courseStore";
import { getVideo } from "@/store/videoStorage";
import { Chapter } from "@/types/course.type";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

export function useEditCourse(courseId: string) {
    const useCourseStore = createCourseStore(courseId);
    const { chapters } = useCourseStore();
    const router = useRouter();

    const { mutate: createChapter, isPending: isCreatingChapter } = useMutation({
        mutationFn: (chapterData: FormData) => createChapterService(chapterData),
        onSuccess: () => {
            toast.success("Curriculum created successfully");
            router.push(`/institution/courses/`);
            deleteCourseStore(courseId);
        },
        onError: (error) => {
            toast.error(error.message);
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

    const UploadCourse = () => {
        createChapter(createFormData(chapters!, courseId));
    }

    return {
        UploadCourse,
        isCreating: isCreatingChapter
    }
}