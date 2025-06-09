import { create, StoreApi, UseBoundStore } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import { EncryptedStorage } from "./encryptedStorage";

type SolveAssessmentType = {
    id: string
    setId: (id: string) => void
    mcqAnswers: Record<string, string>
    setMcqAnswer: (questionId: string, answer: string) => void
    handWrittenAnswers: Record<`handwritten_${string}`, string>
    setHandWrittenAnswer: (questionIdKey: string, handWrittenAnswerKey: string) => void
}

const storeCache: Record<string, UseBoundStore<StoreApi<SolveAssessmentType>>> = {};

export const deleteSolveAssessmentStore = (assessmentId: string) => {
    delete storeCache[assessmentId];
    localStorage.removeItem(`innovate-solve-${assessmentId}`);
}


export const createSolveAssessmentStore = (assessmentId: string) => {
    if (storeCache[assessmentId]) return storeCache[assessmentId];

    const solveAssessmentStore = create<SolveAssessmentType>()(
        persist(
            (set) => ({
                id: assessmentId,
                mcqAnswers: {},
                handWrittenAnswers: {},
                setId: (id: string) => set({ id }),
                setMcqAnswer: (questionId: string, answer: string) => set((state) => ({ mcqAnswers: { ...state.mcqAnswers, [questionId]: answer } })),
                setHandWrittenAnswer: (questionIdKey: string, handWrittenAnswerKey: string) => set((state) => ({ handWrittenAnswers: { ...state.handWrittenAnswers, [questionIdKey]: handWrittenAnswerKey } })),
            }),
            {
                name: `innovate-solve-${assessmentId}`,
                storage: createJSONStorage(() => new EncryptedStorage()),
            }
        )
    )


    storeCache[assessmentId] = solveAssessmentStore;
    return solveAssessmentStore;
}