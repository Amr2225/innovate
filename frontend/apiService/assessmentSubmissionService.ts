import { api } from "./api";

// Store
import { getHandwrittenImage } from "@/store/handwrittenAnswerStorage";

// Utils
import { toast } from "sonner";
import { base64ToFile } from "@/lib/base64ToFile";

// Types
import { SubmissionType } from "@/types/assessmentSubmission.type";

// TODO: extend the type of the store
interface SubmitAssessmentRequest {
    assessmentId: string
    mcqAnswers: Record<string, string>
    handWrittenAnswers: Record<`handwritten_${string}`, string>
}

// TODO: Add the coding question to it
export const submitAssessment = async ({ assessmentId, mcqAnswers, handWrittenAnswers }: SubmitAssessmentRequest) => {
    const formData = new FormData();
    formData.append("mcq_answers", JSON.stringify(mcqAnswers));

    const imagePromises = Object.keys(handWrittenAnswers).map(async (key) => {
        if (key.startsWith("handwritten_")) {
            const handwrittenImage = await getHandwrittenImage(handWrittenAnswers[key as `handwritten_${string}`]);

            if (!handwrittenImage) {
                toast.error("Please Upload the Handwritten Answer")
                return;
            };

            const imageFile = base64ToFile(handwrittenImage);

            const newKey = key.replaceAll("-", "_");
            formData.append(newKey, imageFile);
        }
    });

    // TODO: Try to remove this and see what happends
    await Promise.all(imagePromises);

    const res = await api.post(`/assessmentSubmission/${assessmentId}/`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })

    if (res.status === 201) return true
    throw new Error(res.data.message || "Failed to submit assessment")
};

export const getAssessmentSubmissionForStudent = async (assessmentId: string): Promise<SubmissionType> => {
    const response = await api.get<SubmissionType>(`/assessment/student-grades/${assessmentId}/`, { validateStatus: status => status < 300 });
    return response.data;
}