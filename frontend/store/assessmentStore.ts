import { create, StoreApi, UseBoundStore } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import { EncryptedStorage } from "./encryptedStorage";
import { Answer, Assessment, Question } from "@/types/assessment.type";

export type AssessmentStore = Assessment & {
    sections: {
        id: string;
    }[];
    currentSection: string;
    setCourseId: (courseId: string) => void;

    // Assessment
    updateAssessment: (key: keyof Assessment, value: string) => void;

    // Questions
    addQuestion: () => void;
    setQuestions: (questions: Question[] | ((prev: Question[]) => Question[])) => void;

    updateQuestion: <T extends Question>(questionId: string, key: keyof T, value: string | string[]) => void;
    deleteQuestion: (questionId: string) => void;

    // MCQ 
    addMCQAnswer: (questionId: string) => void;
    setMCQAnswer: (questionId: string, options: Answer[]) => void;
    updateMCQAnswer: (questionId: string, answerId: string, key: keyof Answer, value: string) => void;
    deleteMCQAnswer: (questionId: string, answerId: string) => void;


    // AI Generated MCQ
    setAIGenerateMCQ: (questionId: string, title: string, options: string[], mcqAnswer: string, totalGrade: number) => void;
    updateAIGeneratedMCQAnswer: (questionId: string, questionIndex: number, optionIndex: number, newOptionValue: string) => void;
    updateAIGeneratedMCQQuestion: (questionId: string, questionIndex: number, newQuestionValue: string) => void;
    deleteAIGenerateMCQQueston: (questionId: string, questionTitle: string) => void;
    deleteAIGenerateMCQ: (questionId: string) => void;


    // Sections
    setCurrentSection: (sectionNumber: string) => void;
    addSection: () => void;
    deleteSection: (sectionId: string) => void;
}

const initialState: Pick<AssessmentStore, "id" | "title" | "type" | "questions" | "courseId" | "grade" | "due_date" | "start_date" | "sections" | "currentSection"> = {
    id: "",
    title: "",
    type: "Assignment",
    questions: [],
    courseId: "",
    grade: 0,
    due_date: new Date(),
    start_date: null,
    sections: [{ id: "1" }],
    currentSection: "1",
}

const storeCache: Record<string, UseBoundStore<StoreApi<AssessmentStore>>> = {};

export const deleteAssessmentStore = (assessmentId: string) => {
    delete storeCache[assessmentId];
    localStorage.removeItem(`assessment-store-${assessmentId}`);
}

export const createAssessmentStore = (assessmentId: string) => {
    if (storeCache[assessmentId]) return storeCache[assessmentId];

    const assessmentStore = create<AssessmentStore>()(
        persist(
            (set) => ({
                ...initialState,
                setCourseId: (courseId: string) => {
                    set({ courseId })
                },
                updateAssessment: (key: keyof Assessment, value: string) => {
                    set(() => ({
                        [key]: value
                    }))
                },
                addQuestion: () => {
                    set((state) => ({
                        questions: [...state.questions, {
                            id: Math.random().toString(),
                            title: "New Question",
                            questionType: "",
                            totalGrade: null,
                            sectionNumber: state.currentSection,
                        }]
                    }))
                },
                setQuestions: (questions) => set((state) => ({
                    questions: typeof questions === 'function' ? questions(state.questions) : questions
                })),

                updateQuestion: <T extends Question>(questionId: string, key: keyof T, value: string | string[]) => {
                    set((state) => ({
                        questions: state.questions.map((question) => question.id === questionId ? {
                            ...question,
                            [key]: value
                        } : question)
                    }))
                },
                deleteQuestion: (questionId: string) => {
                    set((state) => ({
                        questions: state.questions.filter((question) => question.id !== questionId)
                    }))
                },


                // AI Generated MCQ
                setAIGenerateMCQ: (questionId: string, title: string, options: string[], mcqAnswer: string, totalGrade: number) => {
                    set((state) => ({
                        questions: state.questions.map((question) => question.id === questionId && question.questionType === "aiMcq" ? {
                            ...question,
                            questions: question.questions ?
                                [...question.questions, {
                                    question: title,
                                    options: options,
                                    correct_answer: mcqAnswer,
                                    total_grade: totalGrade
                                }] : [{
                                    question: title,
                                    options: options,
                                    correct_answer: mcqAnswer,
                                    total_grade: totalGrade
                                }]
                        } : question)
                    }))
                },
                updateAIGeneratedMCQAnswer: (questionId: string, questionIndex: number, optionIndex: number, newOptionValue: string) => {
                    set((state) => ({
                        questions: state.questions.map((question) => question.id === questionId && question.questionType === "aiMcq" ? {
                            ...question,
                            questions:
                                question.questions?.map((questions, index) => index === questionIndex ?
                                    {
                                        ...questions,
                                        options: questions.options?.toSpliced(optionIndex, 1, newOptionValue)
                                    }
                                    : questions)
                        } : question)
                    }))
                },
                updateAIGeneratedMCQQuestion: (questionId: string, questionIndex: number, newQuestionValue: string) => {
                    set((state) => ({
                        questions: state.questions.map((question) => question.id === questionId && question.questionType === "aiMcq" ? {
                            ...question,
                            questions: question.questions?.map((questions, index) => index === questionIndex ?
                                { ...questions, question: newQuestionValue }
                                : questions)
                        } : question)
                    }))
                },
                deleteAIGenerateMCQQueston: (questionId: string, questionTitle: string) => {
                    set((state) => ({
                        questions: state.questions.map((question) => question.id === questionId && question.questionType === "aiMcq" ? {
                            ...question,
                            questions: question.questions?.filter((questions) => questions.question !== questionTitle)
                        } : question)
                    }))
                },
                deleteAIGenerateMCQ: (questionId: string) => {
                    set((state) => ({
                        questions: state.questions.map((question) => question.id === questionId && question.questionType === "aiMcq" ? {
                            ...question,
                            questions: []
                        } : question)
                    }))
                },

                // MCQ
                addMCQAnswer: (questionId: string) => {
                    set((state) => ({
                        questions: state.questions.map((question) => question.id === questionId && question.questionType === "mcq" ? {
                            ...question,
                            options: question.options
                                ? [...question.options, { id: Math.random().toString(), option: "New Answer" }]
                                : [{ id: Math.random().toString(), option: "New Answer" }]
                        } : question)
                    }))
                },
                setMCQAnswer: (questionId: string, options: Answer[]) => {
                    set((state) => ({
                        questions: state.questions.map((question) => question.id === questionId ? {
                            ...question,
                            options: options
                        } : question)
                    }))
                },
                updateMCQAnswer: (questionId: string, answerId: string, key: keyof Answer, value: string) => {
                    set((state) => ({
                        questions: state.questions.map((question) => question.id === questionId && question.questionType === "mcq" ? {
                            ...question,
                            options: question.options!.map((answer) => answer.id === answerId ? { ...answer, [key]: value } : answer)
                        } : question)
                    }))
                },
                deleteMCQAnswer: (questionId: string, answerId: string) => {
                    if (!questionId) return;
                    set((state) => ({
                        questions: state.questions.map((question) => question.id === questionId && question.questionType === "mcq" ? {
                            ...question,
                            options: question.options!.filter((answer) => answer.id !== answerId)
                        } : question)
                    }))
                },
                setCurrentSection: (sectionNumber: string) => {
                    set({
                        currentSection: sectionNumber
                    })
                },
                addSection: () => {
                    set((state) => ({
                        sections: [...state.sections, { id: Math.random().toString() }],
                    }))
                },
                deleteSection: (sectionId: string) => {
                    set((state) => ({
                        // Delete the section from the sections array
                        sections: state.sections.filter((section) => section.id !== sectionId),
                        // Delete the questions that are in the section
                        questions: state.questions.filter((question) => question.sectionNumber !== sectionId)
                    }))
                }
            }),
            {
                name: `assessment-store-${assessmentId}`,
                storage: createJSONStorage(() => new EncryptedStorage()),
            }
        )
    )

    storeCache[assessmentId] = assessmentStore;
    return assessmentStore;
}



