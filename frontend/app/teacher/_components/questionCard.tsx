import React from "react";
import { useParams } from "next/navigation";

// Components
import { Select, SelectContent, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import TypedSelectItem from "./typedSelectItem";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card";
import { DoubleClickEditInput } from "@/components/doubleClickEditInput";

// Types
import { Question } from "@/types/assessment.type";

// Utils
import { motion } from "framer-motion";

// Question Types
import MCQQuestion from "./QuestionTypes/mcq/mcqQuestion";
import DynamicMCQQuestion from "./QuestionTypes/mcq/dynamicMcqQuestion";
import AIGeneratedMcqQuestion from "./QuestionTypes/mcq/AIGeneratedMcqQuestion";
import HandWrittenQuestion from "./QuestionTypes/handwrittenQuestion";
import CodeQuestion from "./QuestionTypes/codeQuestion";

// Icons
import { Info } from "lucide-react";

// Store
import { createAssessmentStore } from "@/store/assessmentStore";

export default function QuestionCard({ question }: { question: Question }) {
  const { assessmentId } = useParams();
  const useAssessmentStore = createAssessmentStore(assessmentId as string);
  const { updateQuestion } = useAssessmentStore();

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2, delay: 0.2 }}
      className='bg-white p-5 text-neutral-600'
    >
      <div className='flex justify-between gap-3 items-center'>
        <div className='flex justify-start gap-3 items-center font-semibold'>
          <QuestionTitle question={question} />
        </div>

        <div className='flex w-[20%] justify-end gap-3 items-center'>
          <Select
            value={question.questionType || ""}
            onValueChange={(value) => updateQuestion(question.id, "questionType", value)}
          >
            <SelectTrigger>
              <SelectValue placeholder='Select Question Type' />
            </SelectTrigger>
            <SelectContent className='w-full'>
              <TypedSelectItem<Question["questionType"]> value='mcq'>MCQ</TypedSelectItem>
              <TypedSelectItem<Question["questionType"]> value='dynamicMcq'>
                Dynamic MCQ
              </TypedSelectItem>
              <TypedSelectItem<Question["questionType"]> value='aiMcq'>
                AI Generatd MCQ
              </TypedSelectItem>
              <TypedSelectItem<Question["questionType"]> value='handWritten'>
                Hand Written
              </TypedSelectItem>
              <TypedSelectItem<Question["questionType"]> value='code'>Code</TypedSelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <Separator className='my-2' />
      {question.questionType === "mcq" && <MCQQuestion question={question} />}
      {question.questionType === "dynamicMcq" && <DynamicMCQQuestion question={question} />}
      {question.questionType === "aiMcq" && <AIGeneratedMcqQuestion question={question} />}
      {question.questionType === "handWritten" && <HandWrittenQuestion question={question} />}
      {question.questionType === "code" && <CodeQuestion question={question} />}
    </motion.div>
  );
}

function QuestionTitle({ question }: { question: Question }) {
  const { assessmentId } = useParams();
  const useAssessmentStore = createAssessmentStore(assessmentId as string);
  const { updateQuestion } = useAssessmentStore();

  if (question.questionType === "aiMcq") {
    return (
      <HoverCard>
        <HoverCardTrigger asChild>
          <h4 className='font-bold text-lg select-none flex items-center gap-1.5'>
            AI Generated MCQ
            <Info className='size-3.5 text-neutral-500' />
          </h4>
        </HoverCardTrigger>
        <HoverCardContent className='w-80'>
          <div className='space-y-2'>
            <h4 className='text-sm font-semibold'>AI Generated MCQ</h4>
            <p className='text-sm text-muted-foreground'>
              This question was automatically generated using AI. The system analyzes the course
              content and creates relevant multiple-choice questions to test student understanding.
            </p>
          </div>
        </HoverCardContent>
      </HoverCard>
    );
  }

  if (question.questionType === "dynamicMcq") {
    return (
      <HoverCard>
        <HoverCardTrigger asChild>
          <h4 className='font-bold text-lg select-none flex items-center gap-1.5'>
            Dynamic MCQ
            <Info className='size-3.5 text-neutral-500' />
          </h4>
        </HoverCardTrigger>
        <HoverCardContent className='w-80'>
          <div className='space-y-2'>
            <h4 className='text-sm font-semibold'>Dynamic MCQ</h4>
            <p className='text-sm text-muted-foreground'>
              This question dynamically generates unique questions for each student. The system
              creates personalized multiple-choice questions based on the course content, ensuring
              each student receives a different set of questions while maintaining consistent
              difficulty levels.
            </p>
          </div>
        </HoverCardContent>
      </HoverCard>
    );
  }

  return (
    <DoubleClickEditInput
      textStyle='text-lg'
      value={question.title}
      setValue={(value: string) => updateQuestion(question.id, "title", value)}
    />
  );
}
