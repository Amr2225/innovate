import React from "react";
import { AssessmentNavbarProvider } from "@/context/assessmentNavbarContext";
import NavBar from "@/components/navbar";

export default function StudentDashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AssessmentNavbarProvider>
      <NavBar />
      {children}
    </AssessmentNavbarProvider>
  );
}
