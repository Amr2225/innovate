interface BaseQuestionSubmission {
    question_id: string;
    question_text: string;
    type: "dynamic_mcq" | "code" | "handwritten" | "mcq";
    score: string;
    max_score: string;
}

// MCQ specific fields
export interface MCQQuestionSubmission extends BaseQuestionSubmission {
    type: "mcq" | "dynamic_mcq";
    options: string[];
    is_correct: boolean;
    student_answer: string;
    correct_answer: string;
}

// Handwritten specific fields
export interface HandwrittenQuestionSubmission extends BaseQuestionSubmission {
    type: "handwritten";
    extracted_text: string;
    feedback: string;
    answer_image: string;
}

type QuestionSubmission = MCQQuestionSubmission | HandwrittenQuestionSubmission

export type SubmissionType = {
    assessment_id: string
    assessment_title: string
    course: string
    total_score: number
    total_max_score: number
    questions: QuestionSubmission[]
}