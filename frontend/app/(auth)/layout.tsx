import NavBar from "@/components/navbar";
import React from "react";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <main>
      <NavBar isAuth />
      {children}
    </main>
  );
}
