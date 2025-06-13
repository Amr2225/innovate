"use client";
import { createContext, Dispatch, SetStateAction, use, useEffect, useState } from "react";

interface AssessmentNavbarContextType {
  courseName: string;
  assessmentTitle: string;
  setCourseName: Dispatch<SetStateAction<string>>;
  setAssessmentTitle: Dispatch<SetStateAction<string>>;
}

const AssessmentNavbarContext = createContext<AssessmentNavbarContextType | undefined>(undefined);

export function AssessmentNavbarProvider({ children }: { children: React.ReactNode }) {
  const [courseName, setCourseName] = useState<string>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("innovate-assessmentCourseName") || "";
    }
    return "";
  });

  const [assessmentTitle, setAssessmentTitle] = useState<string>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("innovate-assessmentTitle") || "";
    }
    return "";
  });

  useEffect(() => {
    localStorage.setItem("innovate-assessmentCourseName", courseName);
  }, [courseName]);

  useEffect(() => {
    localStorage.setItem("innovate-assessmentTitle", assessmentTitle);
  }, [assessmentTitle]);

  return (
    <AssessmentNavbarContext.Provider
      value={{ courseName, assessmentTitle, setCourseName, setAssessmentTitle }}
    >
      {children}
    </AssessmentNavbarContext.Provider>
  );
}

export function useAssessmentNavbar() {
  const context = use(AssessmentNavbarContext);
  if (context === undefined) {
    throw new Error("useAssessmentNavbar must be used within an AssessmentNavbarProvider");
  }
  return context;
}
