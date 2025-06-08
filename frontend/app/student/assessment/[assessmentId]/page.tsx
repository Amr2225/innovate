"use client";
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { getAssessmentQuestionsForStudent } from "@/apiService/assessmentService";
import Loader from "../../dashboard/_components/Loader";

export default function AssessmentPage() {
  const { assessmentId } = useParams();

  const { data: assessment, isLoading } = useQuery({
    queryKey: [`assessment-${assessmentId}`],
    queryFn: () => getAssessmentQuestionsForStudent(assessmentId as string),
  });

  if (isLoading) return <Loader />;

  console.log(assessment);

  return (
    <div>
      <h1>Assessment</h1>
    </div>
  );
}
