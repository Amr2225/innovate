import { SessionProvider } from "next-auth/react";
import React, { Suspense } from "react";

export default function layout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={<h1>Loading....</h1>}>
      <SessionProvider>{children}</SessionProvider>
    </Suspense>
  );
}
