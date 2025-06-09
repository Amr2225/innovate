import { create, StoreApi, UseBoundStore } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import { EncryptedStorage } from "./encryptedStorage";
import { Answer, Assessment, Question } from "@/types/assessment.type";

export type AssessmentStore = Assessment & {
    sections: {
        id: string;
    }[];
    currentSection: number;
    setCourseId: (courseId: string) => void;

    // Assessment
    updateAssessment: (key: keyof Assessment, value: string) => void;

    // Questions
    addQuestion: () => void;
    setQuestions: (questions: Question[] | ((prev: Question[]) => Question[])) => void;

    updateQuestion: (questionId: string, key: keyof Question, value: string | string[]) => void;
    deleteQuestion: (questionId: string) => void;

    // MCQ 
    addMCQAnswer: (questionId: string) => void;
    setMCQAnswer: (questionId: string, options: Answer[]) => void;
    updateMCQAnswer: (questionId: string, answerId: string, key: keyof Answer, value: string) => void;
    deleteMCQAnswer: (questionId: string, answerId: string) => void;


    // AI Generated MCQ
    setAIGenerateMCQ: (questionId: string, title: string, options: string[], mcqAnswer: string) => void;

    // Sections
    setCurrentSection: (sectionNumber: number) => void;
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
    currentSection: 1,
}

const storeCache: Record<string, UseBoundStore<StoreApi<AssessmentStore>>> = {};

export const createAssessmentStore = (courseId: string) => {
    if (storeCache[courseId]) return storeCache[courseId];

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
                            sectionNumber: state.currentSection,
                        }]
                    }))
                },
                setQuestions: (questions) => set((state) => ({
                    questions: typeof questions === 'function' ? questions(state.questions) : questions
                })),

                updateQuestion: (questionId: string, key: keyof Question, value: string | string[]) => {
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
                setAIGenerateMCQ: (questionId: string, title: string, options: string[], mcqAnswer: string) => {
                    set((state) => ({
                        questions: state.questions.map((question) => question.id === questionId ? {
                            ...question,
                            questions: [{
                                question: title,
                                options: options,
                                correct_answer: mcqAnswer
                            }]
                        } : question)
                    }))
                },
                addMCQAnswer: (questionId: string) => {
                    set((state) => ({
                        questions: state.questions.map((question) => question.id === questionId ? {
                            ...question,
                            // options: question.options!.push({ id: Math.random().toString(), option: "New Answer" })
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
                        questions: state.questions.map((question) => question.id === questionId ? {
                            ...question,
                            options: question.options!.map((answer) => answer.id === answerId ? { ...answer, [key]: value } : answer)
                        } : question)
                    }))
                },
                deleteMCQAnswer: (questionId: string, answerId: string) => {
                    if (!questionId) return;
                    set((state) => ({
                        questions: state.questions.map((question) => question.id === questionId ? {
                            ...question,
                            options: question.options!.filter((answer) => answer.id !== answerId)
                        } : question)
                    }))
                },
                setCurrentSection: (sectionNumber: number) => {
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
                        questions: state.questions.filter((question) => question.sectionNumber !== Number(sectionId))
                    }))
                }
            }),
            {
                name: `assessment-store-${courseId}`,
                storage: createJSONStorage(() => new EncryptedStorage()),
            }
        )
    )

    storeCache[courseId] = assessmentStore;
    return assessmentStore;
}



