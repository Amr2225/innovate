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
}