import React from "react";
import { AssessmentNavbarProvider } from "@/context/assessmentNavbarContext";

export default function AssessmentLayout({ children }: { children: React.ReactNode }) {
  return (
    <AssessmentNavbarProvider>
      {/* <h1>Assessment Layout</h1> */}
      {children}
    </AssessmentNavbarProvider>
  );
}
