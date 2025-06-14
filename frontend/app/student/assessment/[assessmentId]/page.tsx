"use client";
import React from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

// Services
import { getAssessmentQuestionsForStudent } from "@/apiService/assessmentService";
import { submitAssessment } from "@/apiService/assessmentSubmissionService";

// Components
import Loader from "@/components/Loader";
import { Button } from "@/components/ui/button";

// Local Components
import { NavBar } from "@/app/student/assessment/_components/Navbar";
import MCQQuestion from "@/app/student/assessment/_components/mcqQuestion";
import HandWrittenQuestion from "@/app/student/assessment/_components/handWrittenQuestion";

// Query
import { useQuery } from "@tanstack/react-query";
import { useMutation } from "@tanstack/react-query";

// Store
import {
  createSolveAssessmentStore,
  deleteSolveAssessmentStore,
} from "@/store/solveAssessmentStore";
import { ArrowLeft, Loader2 } from "lucide-react";
import { toast } from "sonner";

export default function AssessmentPage() {
  const { assessmentId } = useParams();

  const router = useRouter();
  const useSolveAssessmentStore = createSolveAssessmentStore(assessmentId as string);
  const { handWrittenAnswers, mcqAnswers } = useSolveAssessmentStore();

  //TODO: Add logic if the student already submitted an assessment can't access this page
  const {
    data: assessment,
    isLoading,
    error,
  } = useQuery({
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
      router.push(`/student/assessment/${assessmentId}/submission`);
      deleteSolveAssessmentStore(assessmentId as string);
    },
  });

  const handleSubmitAssessment = () => {
    if (
      Object.keys(mcqAnswers).length + Object.keys(handWrittenAnswers).length !==
      assessment?.questions.length
    ) {
      toast.error("Please answer all of the questions");
      return;
    }

    submitAssessmentMutation();
  };

  if (error)
    return (
      <div className='w-full min-h-screen bg-neutral-50'>
        <div className='w-full h-[calc(100vh-7rem)] flex justify-center items-center'>
          <div className='w-[85%] mx-auto bg-white rounded-lg p-8 border shadow-sm'>
            <div className='flex flex-col items-center justify-center gap-4'>
              <p className='text-neutral-600 text-center'>{error.message}</p>
              <Button asChild>
                <Link href={`/student/dashboard`}>
                  <ArrowLeft className='size-4 mr-2' />
                  Go Back
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
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
              onClick={handleSubmitAssessment}
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
