import { AIGeneratedMCQQuestion, Assessment, DynamicMCQQuestion, HandWrittenQuestion, MCQQuestion, Question } from "@/types/assessment.type";
import { api } from "./api";

//------------------------
//  Creating Assessment
//------------------------
export const createAssessment = async (assessment: Pick<Assessment, "courseId" | "title" | "type" | "due_date" | "start_date" | "grade">) => {
    const response = await api.post<{ detail?: string }>("/assessment/", {
        ...assessment,
        courseId: undefined,
        course: assessment.courseId
    });

    if (response.status === 201) return true;
    throw new Error(response.data?.detail || "Failed to create assessment");
};

export const updateAssessment = async (assessment: Pick<Assessment, "id" | "courseId" | "title" | "type" | "start_date" | "due_date" | "grade">) => {
    const response = await api.put<{ message: string }>(`/assessment/${assessment.id}/`, {
        course: assessment.courseId,
        title: assessment.title,
        type: assessment.type,
        start_date: assessment.start_date,
        due_date: assessment.due_date,
        grade: assessment.grade
    });

    if (response.status === 200) return true;
    throw new Error(response.data?.message || "Failed to update assessment");
}

export const deleteAssessment = async (assessmentId: string) => {
    const response = await api.delete<{ detail: string }>(`/assessment/${assessmentId}/`);

    if (response.status === 204) return true
    throw new Error(response.data?.detail || "Failed to delete assessment")
}

// Handwritten
export const handwrittenQuestion = async ({ question, assessmentId }: { question: Pick<HandWrittenQuestion, "title" | "handWrittenAnswerKey" | "totalGrade">, assessmentId: string }) => {
    const response = await api.post<Question>("/handwrittenQuestion/questions/", {
        assessment: assessmentId,
        question_text: question.title,
        answer_key: question.handWrittenAnswerKey,
        max_grade: question.totalGrade
    });

    if (response.status === 201) return response.data;
    throw new Error("Failed to create handwritten question");
}

// Dynamic MCQ
export const dynamicMcqQuestion = async ({ question, assessmentId, sections }: { question: DynamicMCQQuestion, assessmentId: string, sections: { id: string }[] }) => {
    const response = await api.post<{ message: string }>(`/dynamicMCQ/${assessmentId}/`, {
        section_number: sections.findIndex((section) => section.id === question.sectionNumber) + 1,
        lecture_ids: question.lectures,
        difficulty: question.difficulty,
        total_grade: question.totalGrade,
        number_of_questions: question.numberOfQuestions,
        context: question.context
    });

    if (response.status === 201) return true
    throw new Error(response.data.message || "Failed to create dynamic mcq question");
}

interface AIGeneratedMcqQuestionResponse {
    question: string
    options: string[]
    correct_answer: string
}

// AI Generated MCQ
export const aiGeneratedMcqQuestion = async ({ question }: { question: AIGeneratedMCQQuestion }) => {
    const response = await api.post<{ mcqs: AIGeneratedMcqQuestionResponse[], message?: string }>(`/mcqQuestion/generate-from-lectures/`, {
        question: question.title,
        num_options: question.numberOfChoices,
        difficulty: question.difficulty,
        number_of_questions: question.numberOfQuestions,
        lecture_ids: question.lectures
    });

    if (response.status === 200) return response.data.mcqs;
    throw new Error(response.data.message || "Failed to create dynamic mcq question");
}

// Save AI Generated MCQ
export const saveAIGeneratedMcqQuestion = async ({ question, assessmentId, sections }: { question: AIGeneratedMCQQuestion, assessmentId: string, sections: { id: string }[] }) => {
    const response = await api.post<{ message: string }>(`/mcqQuestion/save-generated-mcqs/${assessmentId}/`, {
        assessment: assessmentId,
        mcqs: question.questions,
        question_grade: question.totalGrade,
        section_number: sections.findIndex((section) => section.id === question.sectionNumber) + 1
    });

    if (response.status === 201) return true
    throw new Error(response.data.message || "Failed to save ai generated mcq question");
}


// MCQ
export const mcqQuestion = async ({ question, assessmentId, sections }: { question: Pick<MCQQuestion, "title" | "options" | "totalGrade" | "correctOption" | "sectionNumber">, assessmentId: string, sections: { id: string }[] }) => {
    const response = await api.post<Question>(`/mcqQuestion/${assessmentId}/`, {
        assessment: assessmentId,
        question: question.title,
        options: question.options.map((option) => option.option),
        answer_key: question.correctOption,
        question_grade: question.totalGrade,
        section_number: sections.findIndex((section) => section.id === question.sectionNumber) + 1
    });

    if (response.status === 201) return true;
    throw new Error("Failed to create mcq question");
}


// ----------------------------
//  Getting Assessment
// ----------------------------
export interface AssessmentResponse extends Assessment {
    has_submitted: boolean;
    course: string;
    course_description: string;
}

interface GetAssessmentResponse {
    data: AssessmentResponse[];
    previous: number | null;
    next: number | null;
    page: number;
    page_size: number;
    total_pages: number;
    total_items: number;
}

interface QuestionResponse extends Omit<Question, 'options' | 'questionType'> {
    type: "dynamic_mcq" | "code" | "handwritten" | "mcq"
    question: string;
    options: string[];
}

export const getAssessment = async ({ pageParam, page_size, type, due_date, title }: { pageParam?: number, page_size?: number, type?: string, due_date?: string, title?: string }): Promise<GetAssessmentResponse> => {
    const response = await api.get<GetAssessmentResponse>(`/assessment/`, { params: { page: pageParam, page_size, type, due_date, title } });

    if (response.status === 200) return response.data;
    throw new Error("Failed to get assessment");
}

export const getAssessmentQuestionsForStudent = async (assessmentId: string) => {
    const response = await api.get<{ questions: QuestionResponse[], assessment: AssessmentResponse, detail: string }>(`/assessment/${assessmentId}/student-questions/`);

    if (response.status === 200) return response.data;
    throw new Error(response.data.detail || "Failed to get assessment questions for student");
}

export const getAssessmentByCourseId = async (courseId: string) => {
    const response = await api.get<{ data: AssessmentResponse[] }>(`/assessment/course/${courseId}/`);
    return response.data;
}
