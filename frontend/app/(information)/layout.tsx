import Footer from "@/components/Footer";
import NavBar from "@/components/navbar";
import React from "react";

export default function InformationPagesLayout({ children }: { children: React.ReactNode }) {
  return (
    <main>
      <NavBar />
      {children}
      <hr className='my-5 border-none ' />
      <Footer />
    </main>
  );
}
