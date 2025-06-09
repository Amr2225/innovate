"use client";
import React from "react";
import { useParams } from "next/navigation";

// Services
import { getAssessmentQuestionsForStudent } from "@/apiService/assessmentService";
import { submitAssessment } from "@/apiService/assessmentSubmissionService";

// Components
import Loader from "@/components/Loader";
import { Button } from "@/components/ui/button";

// Local Components
import { NavBar } from "../_components/Navbar";
import MCQQuestion from "../_components/mcqQuestion";
import HandWrittenQuestion from "../_components/handWrittenQuestion";

// Query
import { useQuery } from "@tanstack/react-query";
import { useMutation } from "@tanstack/react-query";

// Store
import {
  createSolveAssessmentStore,
  deleteSolveAssessmentStore,
} from "@/store/solveAssessmentStore";
import { Loader2 } from "lucide-react";

export default function AssessmentPage() {
  const { assessmentId } = useParams();
  const useSolveAssessmentStore = createSolveAssessmentStore(assessmentId as string);
  const { handWrittenAnswers, mcqAnswers } = useSolveAssessmentStore();

  //TODO: Add logic if the student already submitted an assessment can't access this page
  const { data: assessment, isLoading } = useQuery({
    queryKey: [`assessment-${assessmentId}`],
    queryFn: () => getAssessmentQuestionsForStudent(assessmentId as string),
  });

  const { mutate: submitAssessmentMutation, isPending: isSubmitting } = useMutation({
    mutationFn: () =>
      submitAssessment({
        assessmentId: assessmentId as string,
        mcqAnswers: mcqAnswers,
        handWrittenAnswers: handWrittenAnswers,
      }),

    onSuccess: () => {
      deleteSolveAssessmentStore(assessmentId as string);
    },
  });

  if (isLoading || !assessment || !assessmentId) return <Loader />;

  return (
    <div className='w-full'>
      <NavBar
        assessmentTitle={assessment.assessment.title}
        courseName={assessment.assessment.course}
        startTime={assessment.assessment.start_date!}
        endTime={assessment.assessment.due_date!}
      />
      <div className='bg-neutral-50 rounded-lg p-2 w-full h-full min-h-[calc(100vh-7rem)] pt-4'>
        <div className='w-[85%] mx-auto bg-white rounded-lg p-4 border'>
          {assessment.questions.map((question, index) => (
            <div key={question.id}>
              <header className='border-b border-neutral-200 p-2'>
                <h1 className='text-2xl font-bold'>Question {index + 1}</h1>
              </header>
              {(question.type === "dynamic_mcq" || question.type === "mcq") && (
                <MCQQuestion
                  assessmentId={assessmentId as string}
                  questionId={question.id}
                  question={question.question}
                  options={question.options!}
                />
              )}
              {question.type === "handwritten" && (
                <HandWrittenQuestion question={question.question} questionId={question.id} />
              )}
            </div>
          ))}
          <div className='w-full flex justify-end items-center'>
            <Button
              size='lg'
              className='text-base font-semibold w-[20%]'
              onClick={() => submitAssessmentMutation()}
              disabled={isSubmitting}
            >
              {isSubmitting ? <Loader2 className='animate-spin size-4' /> : "Submit"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
