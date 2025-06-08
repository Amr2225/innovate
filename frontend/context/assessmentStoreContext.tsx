"use client";

import { AssessmentStore } from "@/store/assessmentStore";
import { createContext, use } from "react";
import { StoreApi, UseBoundStore } from "zustand";
import { useParams } from "next/navigation";
import { createAssessmentStore } from "@/store/assessmentStore";

export const AssessmentStoreContext = createContext<UseBoundStore<
  StoreApi<AssessmentStore>
> | null>(null);

export function AssessmentStoreProvider({ children }: { children: React.ReactNode }) {
  const { courseId } = useParams();
  const assessmentStore = createAssessmentStore(courseId as string);
  return (
    <AssessmentStoreContext.Provider value={assessmentStore}>
      {children}
    </AssessmentStoreContext.Provider>
  );
}

export function useAssessmentStore() {
  const assessmentStore = use(AssessmentStoreContext);
  if (!assessmentStore) {
    throw new Error("useAssessmentStore must be used within a AssessmentStoreProvider");
  }
  return assessmentStore;
}
