// "use client";
// import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
// import React from "react";

// export default function VerifyEmailLayout({ children }: { children: React.ReactNode }) {
//   const queryClient = new QueryClient();
//   return (
//     <QueryClientProvider client={queryClient}>
//       <div>{children}</div>
//     </QueryClientProvider>
//   );
// }

import React from "react";

export default function Layout({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>;
}
