export type Assessment = {
    id: string;
    title: string;
    type: "assignment" | "quiz" | "exam";
    questions: Question[];
    courseId: string;
    grade: number;
    dueDate: Date;
    startDate: Date;
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

    // For Dynamic MCQ
    context?: string;
    lectures?: string[];
    difficulty?: number;
    totalGrade?: number;
    numberOfQuestions?: number;
}