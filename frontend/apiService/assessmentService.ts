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
        section_number: question.sectionNumber,
        lecture_ids: question.lectures,
        difficulty: question.difficulty,
        total_grade: question.totalGrade,
        number_of_questions: question.numberOfQuestions
    });

    if (response.status === 201) return response.data;
    throw new Error("Failed to create dynamic mcq question");
}

interface AIGeneratedMcqQuestionResponse {
    question: string
    options: string[]
    correct_answer: string
}

// AI Generated MCQ
export const aiGeneratedMcqQuestion = async ({ question }: { question: Pick<Question, "title" | "numberOfChoices" | "difficulty" | "lectures"> }) => {
    const response = await api.post<{ mcqs: AIGeneratedMcqQuestionResponse[] }>(`/mcqQuestion/generate-from-lectures/`, {
        question: question.title,
        num_options: question.numberOfChoices,
        difficulty: question.difficulty,
        num_questions_per_lecture: 4,
        lecture_ids: question.lectures
    });
    console.log("data", response.data, response.status);

    if (response.status === 200) return response.data.mcqs;
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
    course: string;
}

interface QuestionResponse extends Omit<Question, 'options' | 'questionType'> {
    type: "dynamic_mcq" | "code" | "handwritten" | "mcq"
    question: string;
    options: string[];
}

export const getAssessment = async () => {
    const response = await api.get<{ data: AssessmentResponse[] }>(`/assessment/`, { params: { page_size: 200, type: "Assignment" } });

    if (response.status === 200) return response.data;
    throw new Error("Failed to get assessment");
}

export const getAssessmentQuestionsForStudent = async (assessmentId: string) => {
    const response = await api.get<{ questions: QuestionResponse[], assessment: AssessmentResponse }>(`/assessment/${assessmentId}/student-questions/`);
    return response.data;
}

export const getAssessmentByCourseId = async (courseId: string) => {
    const response = await api.get<{ data: AssessmentResponse[] }>(`/assessment/course/${courseId}/`);
    return response.data;
}
