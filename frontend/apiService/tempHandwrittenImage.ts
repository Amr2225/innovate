import axios from "axios";

export const addTempHandwrittenImage = async ({ formData, assessmentId, questionId, token }: { formData: FormData, assessmentId: string, questionId: string, token: string }) => {
    const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/assessment/temp-handwritten-image/${assessmentId}/${questionId}/`, formData, {
        headers: {
            "Content-Type": "multipart/form-data",
            "Authorization": `Bearer ${token}`
        },
    });
    return response.status === 200;
}



