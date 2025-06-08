"use client";
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { getAssessmentQuestionsForStudent } from "@/apiService/assessmentService";
import Loader from "@/components/Loader";

// Local Components
import { NavBar } from "../_components/Navbar";
import MCQQuestion from "../_components/mcqQuestion";
import HandWrittenQuestion from "../_components/handWrittenQuestion";
export default function AssessmentPage() {
  const { assessmentId } = useParams();

  const { data: assessment, isLoading } = useQuery({
    queryKey: [`assessment-${assessmentId}`],
    queryFn: () => getAssessmentQuestionsForStudent(assessmentId as string),
  });

  if (isLoading || !assessment) return <Loader />;

  console.log(assessment.questions[0].id);

  return (
    <div className='w-full'>
      <NavBar
        assessmentTitle={assessment.assessment.title}
        courseName={assessment.assessment.course}
      />
      <div className='bg-neutral-50 rounded-lg p-2 w-full h-full min-h-[calc(100vh-7rem)] pt-4'>
        <div className='w-[85%] mx-auto bg-white rounded-lg p-4 border'>
          {assessment.questions.map((question, index) => (
            <div key={question.id}>
              <header className='border-b border-neutral-200 p-2'>
                <h1 className='text-2xl font-bold'>Question {index + 1}</h1>
              </header>
              {(question.type === "dynamic_mcq" || question.type === "mcq") && (
                <MCQQuestion question={question.question} options={question.options!} />
              )}
              {question.type === "handwritten" && (
                <HandWrittenQuestion question={question.question} questionId={question.id} />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
