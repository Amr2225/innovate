"use client";
import React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export default function BackButton() {
  const router = useRouter();
  return <Button onClick={() => router.back()}>Go Back</Button>;
}
