import React, { useRef, useState } from "react";

// Components
import { Select, SelectContent, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import TypedSelectItem from "./typedSelectItem";

// Types
import { Question } from "@/types/assessment.type";

// Store
import { useAssessmentStore } from "@/store/assessmentStore";

// Utils
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

// Question Types
import MCQQuestion from "./QuestionTypes/mcq/mcqQuestion";
import DynamicMCQQuestion from "./QuestionTypes/mcq/dynamicMcqQuestion";
import AIGeneratedMcqQuestion from "./QuestionTypes/mcq/AIGeneratedMcqQuestion";
import HandWrittenQuestion from "./QuestionTypes/handwrittenQuestion";
import CodeQuestion from "./QuestionTypes/codeQuestion";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card";
import { Info } from "lucide-react";

export default function QuestionCard({ question }: { question: Question }) {
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
            value={question.questionType as string}
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
                HandWritten
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

// TODO: Make this a component
export function CustomEditInput({
  value,
  setValue,
  textStyle,
}: {
  value: string;
  setValue: (value: string) => void;
  textStyle?: string;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    if (e.target.value.trim() === "") return;

    setValue(e.target.value);
    setIsEditing(false);
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const inputValue = inputRef.current?.value;
    if (!inputValue) return;
    if (inputValue.trim() === "") return;

    setValue(inputValue);
    setIsEditing(false);
  };

  return (
    <span className='font-bold '>
      {isEditing ? (
        <form className='flex items-center gap-2' onSubmit={handleSubmit}>
          <Input
            className={cn("w-full", textStyle)}
            defaultValue={value}
            ref={inputRef}
            onBlur={handleBlur}
            autoFocus
          />
          <div className='flex items-center gap-2'>
            {/* <Button variant='secondary' type='button' className='px-3 text-xs font-semibold'>
              Cancel
            </Button> */}
            <Button variant='default' type='submit' className='px-3 text-xs font-semibold'>
              Save
            </Button>
          </div>
        </form>
      ) : (
        <h4
          onDoubleClick={() => setIsEditing(true)}
          className={cn("font-bold text-sm select-none", textStyle)}
        >
          {value}
        </h4>
      )}
    </span>
  );
}

function QuestionTitle({ question }: { question: Question }) {
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
    <CustomEditInput
      textStyle='text-lg'
      value={question.title}
      setValue={(value) => updateQuestion(question.id, "title", value)}
    />
  );
}
