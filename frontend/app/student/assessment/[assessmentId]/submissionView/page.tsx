"use client";
import { useParams } from "next/navigation";

// Components
import { NavBar } from "../../_components/Navbar";
import Loader from "@/components/Loader";

// Questions Components
import MCQQuestionSubmission from "../../_components/submission/mcqQuestionSubmision";
import HandwrittenSubmission from "../../_components/submission/handwrittenSubmission";

// API Serivces
import { useQuery } from "@tanstack/react-query";
import { getAssessmentSubmissionForStudent } from "@/apiService/assessmentSubmissionService";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function SubmissionViewPage() {
  const { assessmentId } = useParams();

  const {
    data: submission,
    isLoading,
    error,
  } = useQuery({
    queryKey: [`assessment-submission-${assessmentId}`],
    queryFn: () => getAssessmentSubmissionForStudent(assessmentId as string),
  });

  if (error) return <div className='text-red-500'>{error.message}</div>;
  if (isLoading || !submission) return <Loader />;

  console.log(submission);

  return (
    <div className='w-full'>
      <NavBar
        assessmentTitle={submission.assessment_title}
        courseName={submission.course}
        totalScore={submission.total_max_score}
        score={submission.total_score}
      />
      <div className='bg-neutral-50 rounded-lg p-2 w-full h-full min-h-[calc(100vh-7rem)] pt-4'>
        <div className='w-[85%] mx-auto'>
          <Button variant='link' asChild className='pl-0'>
            <Link href={`/student/dashboard`}>
              <ArrowLeft className='size-4' />
              Go Back to Dashbord
            </Link>
          </Button>
        </div>
        <div className='w-[85%] mx-auto bg-white rounded-lg p-4 border'>
          {submission.questions.map((question, index) => (
            <div key={question.question_id}>
              <header className='border-b border-neutral-200 p-2'>
                <h1 className='text-2xl font-bold'>Question {index + 1}</h1>
              </header>
              {(question.type === "dynamic_mcq" || question.type === "mcq") && (
                <MCQQuestionSubmission
                  question_text={question.question_text}
                  options={question.options}
                  student_answer={question.student_answer}
                  correct_answer={question.correct_answer}
                  type={question.type}
                  is_correct={question.is_correct}
                  question_id={question.question_id}
                  score={question.score}
                  max_score={question.max_score}
                />
              )}
              {question.type === "handwritten" && (
                <HandwrittenSubmission
                  question_text={question.question_text}
                  answer_image={question.answer_image}
                  extracted_text={question.extracted_text}
                  feedback={question.feedback}
                  score={question.score}
                  max_score={question.max_score}
                  question_id={question.question_id}
                  type={question.type}
                />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
