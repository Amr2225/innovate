import { SessionProvider } from "next-auth/react";
import React from "react";

export default function RegisterLayout({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <div>{children}</div>
    </SessionProvider>
  );
}
