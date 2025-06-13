"use client";
import { createContext, Dispatch, SetStateAction, use, useState } from "react";

interface BreadcrumbContextType {
  customPathnames: string;
  metadata: Map<string, string>;
  setCustomPathnames: Dispatch<SetStateAction<string>>;
  setNewMetadata: (key: string, value: string) => void;
}

const BreadcrumbContext = createContext<BreadcrumbContextType | undefined>(undefined);

export function BreadcrumbProvider({ children }: { children: React.ReactNode }) {
  const [customPathnames, setCustomPathnames] = useState<string>("");
  const [metadata, setMetadata] = useState<Map<string, string>>(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("breadcrumbMetadata");
      return stored ? new Map(JSON.parse(stored)) : new Map();
    }
    return new Map();
  });

  const setNewMetadata = (key: string, value: string) => {
    setMetadata((prev) => prev.set(key, value));
    localStorage.setItem("breadcrumbMetadata", JSON.stringify(Array.from(metadata.entries())));
  };

  return (
    <BreadcrumbContext.Provider
      value={{ customPathnames, metadata, setCustomPathnames, setNewMetadata }}
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
