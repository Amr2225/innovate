"use client";
import { createContext, Dispatch, SetStateAction, use, useState } from "react";

interface BreadcrumbContextType {
  customPathnames: string;
  setMetadata: Dispatch<SetStateAction<Map<string, string>>>;
  metadata: Map<string, string>;
  setCustomPathnames: Dispatch<SetStateAction<string>>;
}

const BreadcrumbContext = createContext<BreadcrumbContextType | undefined>(undefined);

export function BreadcrumbProvider({ children }: { children: React.ReactNode }) {
  const [customPathnames, setCustomPathnames] = useState<string>("");
  const [metadata, setMetadata] = useState<Map<string, string>>(new Map());

  return (
    <BreadcrumbContext.Provider
      value={{ customPathnames, metadata, setCustomPathnames, setMetadata }}
    >
      {children}
    </BreadcrumbContext.Provider>
  );
}

export function useBreadcrumb() {
  const context = use(BreadcrumbContext);
  if (context === undefined) {
    throw new Error("useBreadcrumb must be used within a BreadcrumbProvider");
  }
  return context;
}
