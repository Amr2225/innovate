import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import { EncryptedStorage } from "./encryptedStorage";
import { Answer, Assessment, Question } from "@/types/assessment.type";


type AssessmentStore = Assessment & {
    sections: {
        id: string;
    }[];
    currentSection: number;
    setCourseId: (courseId: string) => void;

    // Questions
    addQuestion: () => void;
    setQuestions: (questions: Question[] | ((prev: Question[]) => Question[])) => void;

    updateQuestion: (questionId: string, key: keyof Question, value: string) => void;
    deleteQuestion: (questionId: string) => void;

    addMCQAnswer: (questionId: string) => void;
    setMCQAnswer: (questionId: string, options: Answer[]) => void;
    updateMCQAnswer: (questionId: string, answerId: string, key: keyof Answer, value: string) => void;
    deleteMCQAnswer: (questionId: string, answerId: string) => void;

    setCurrentSection: (sectionNumber: number) => void;
    addSection: () => void;
    deleteSection: (sectionId: string) => void;
}

const initialState: Pick<AssessmentStore, "id" | "title" | "type" | "questions" | "courseId" | "grade" | "dueDate" | "startDate" | "sections" | "currentSection"> = {
    id: "",
    title: "",
    type: "assignment",
    questions: [],
    courseId: "",
    grade: 0,
    dueDate: new Date(),
    startDate: new Date(),
    sections: [{ id: "1" }],
    currentSection: 1,
}


export const useAssessmentStore = create<AssessmentStore>()(
    persist(
        (set) => ({
            ...initialState,
            setCourseId: (courseId: string) => {
                set({ courseId })
            },
            addQuestion: () => {
                set((state) => ({
                    questions: [...state.questions, {
                        id: Math.random().toString(),
                        title: "New Question",
                        questionType: "",
                        sectionNumber: state.currentSection
                    }]
                }))
            },
            setQuestions: (questions) => set((state) => ({
                questions: typeof questions === 'function' ? questions(state.questions) : questions
            })),

            updateQuestion: (questionId: string, key: keyof Question, value: string) => {
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
            name: "assessment-store",
            storage: createJSONStorage(() => new EncryptedStorage()),
        }
    )
)
