"use client";
import { useBreadcrumb } from "@/context/breadcrumbsContext";
import { useParams } from "next/navigation";
import React, { useEffect, useState } from "react";

export default function CourseTitle() {
  const { courseId } = useParams();
  const { metadata } = useBreadcrumb();

  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) return <h1></h1>;

  return (
    <h1 className='text-2xl font-bold'>
      {metadata.has(courseId as string) ? metadata.get(courseId as string) : "Watch Course"}
    </h1>
  );
}
