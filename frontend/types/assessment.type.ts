export type Assessment = {
    id: string;
    title: string;
    type: "Assignment" | "Quiz" | "Exam";
    questions: Question[];
    courseId: string;
    grade: number;
    due_date: Date;
    start_date: Date | null;
}

export type Answer = {
    id: string;
    option: string;
}

// export interface QuestionBase {
//     id: string;
//     title: string;
//     questionType: "mcq" | "handWritten" | "code" | "dynamicMcq" | "aiMcq" | ""
//     totalGrade: number | null;
//     sectionNumber: number;
// }

// export interface MCQQuestion extends QuestionBase {
//     questionType: "mcq";
//     mcqAnswer: string;
//     options: Answer[];
//     correctOption: string;
// }

// export interface DynamicMCQQuestion extends QuestionBase {
//     questionType: "dynamicMcq";
//     context: string;
//     lectures: string[];
//     difficulty: "1" | "2" | "3" | "4" | "5" | null;
//     numberOfQuestions: number;
//     numberOfChoices: number;
// }

// export interface AIGeneratedMCQQuestion extends QuestionBase {
//     questionType: "aiMcq";
//     difficulty: "1" | "2" | "3" | "4" | "5" | null;
//     numberOfQuestions: number;
//     numberOfChoices: number;
//     options: Answer[];
//     correctOption: string;
// }

// export interface HandWrittenQuestion extends QuestionBase {
//     questionType: "handWritten";
//     handWrittenAnswerKey: string;
// }

// export interface CodeQuestion extends QuestionBase {
//     questionType: "code";
//     codeAnswerKey: string;
// }

// export type Question = MCQQuestion | DynamicMCQQuestion | AIGeneratedMCQQuestion | HandWrittenQuestion | CodeQuestion;




export type Question = {
    id: string;
    title: string;
    options?: Answer[];
    questionType: "mcq" | "handWritten" | "code" | "dynamicMcq" | "aiMcq" | ""
    correctOption?: string;
    mcqAnswer?: string;
    handWrittenAnswerKey?: string;
    sectionNumber: number;
    totalGrade?: number;

    // For Dynamic MCQ
    context?: string;
    lectures?: string[];
    difficulty?: "1" | "2" | "3" | "4" | "5" | null;
    numberOfQuestions?: number;
    numberOfChoices?: number;


    // For AI Generated MCQ
    questions?: {
        question: string;
        options: string[];
        correct_answer: string;
    }[];
    questionDifficulty?: "Very Easy" | "Easy" | "Medium" | "Hard" | "Very Hard"

}