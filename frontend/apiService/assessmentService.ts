import { Assessment, Question } from "@/types/assessment.type";
import { api } from "./api";

//------------------------
//  Creating Assessment
//------------------------
export const createAssessment = async (assessment: Pick<Assessment, "courseId" | "title" | "type" | "due_date" | "start_date" | "grade">) => {
    const response = await api.post<Assessment>("/assessment/", {
        ...assessment,
        courseId: undefined,
        course: assessment.courseId
    });

    if (response.status === 201) return response.data;
    throw new Error("Failed to create assessment");
};

// Handwritten
export const handwrittenQuestion = async ({ question, assessmentId }: { question: Pick<Question, "title" | "handWrittenAnswerKey" | "totalGrade">, assessmentId: string }) => {
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
export const dynamicMcqQuestion = async ({ question, assessmentId }: { question: Pick<Question, "totalGrade" | "sectionNumber" | "context" | "lectures" | "difficulty" | "numberOfQuestions">, assessmentId: string }) => {
    const response = await api.post<Question>(`/dynamicMCQ/assessments/${assessmentId}/`, {
        section_number: "1",
        context: question.context,
        lecture_ids: question.lectures,
        difficulty: question.difficulty,
        total_grade: question.totalGrade,
        number_of_questions: question.numberOfQuestions
    });

    if (response.status === 201) return response.data;
    throw new Error("Failed to create dynamic mcq question");
}


// MCQ
export const mcqQuestion = async ({ question, assessmentId }: { question: Pick<Question, "title" | "options" | "totalGrade" | "mcqAnswer" | "sectionNumber">, assessmentId: string }) => {
    const response = await api.post<Question>('/mcqQuestion/mcq-questions/', {
        assessment: assessmentId,
        question: question.title,
        options: question.options,
        answer_key: question.mcqAnswer,
        question_grade: question.totalGrade,
        section_number: question.sectionNumber
    });

    if (response.status === 201) return response.data;
    throw new Error("Failed to create mcq question");
}


// ----------------------------
//  Getting Assessment
// ----------------------------
interface AssessmentResponse extends Assessment {
    has_submitted: boolean;
}

export const getAssessment = async () => {
    const response = await api.get<{ data: AssessmentResponse[] }>(`/assessment/`);

    if (response.status === 200) return response.data;
    throw new Error("Failed to get assessment");
}

export const getAssessmentQuestionsForStudent = async (assessmentId: string) => {
    const response = await api.get<{ questions: Question[] }>(`/assessment/${assessmentId}/student-questions/`);
    return response.data;
}

export const getAssessmentByCourseId = async (courseId: string) => {
    const response = await api.get<{ data: AssessmentResponse[] }>(`/assessment/course/${courseId}/`);
    return response.data;
}
