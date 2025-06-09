import { create, StoreApi, UseBoundStore } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import { EncryptedStorage } from "./encryptedStorage";

type SolveAssessmentType = {
    id: string
    setId: (id: string) => void
}

const storeCache: Record<string, UseBoundStore<StoreApi<SolveAssessmentType>>> = {};


export const createSolveAssessmentStore = (assessmentId: string) => {
    if (storeCache[assessmentId]) return storeCache[assessmentId];

    const solveAssessmentStore = create<SolveAssessmentType>()(
        persist(
            (set) => ({
                id: assessmentId,
                setId: (id: string) => set({ id })
            }),
            {
                name: `innovate-solve-${assessmentId}`,
                storage: createJSONStorage(() => new EncryptedStorage()),
            }
        )
    )


    storeCache[assessmentId] = solveAssessmentStore;
    return assessmentId;
}