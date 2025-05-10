import NavBar from "@/components/navbar";
import React from "react";

export default function StudentDashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <NavBar />
      {children}
    </>
  );
}
