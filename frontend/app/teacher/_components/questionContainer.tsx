import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { createAssessmentStore } from "@/store/assessmentStore";
import { Question } from "@/types/assessment.type";
import { Reorder, useDragControls } from "framer-motion";
import { Menu, Trash2 } from "lucide-react";
import React, { useState } from "react";
import QuestionCard from "./questionCard";
import { useParams } from "next/navigation";
export default function QuestionContainer({
  question,
  questionNumber,
}: {
  question: Question;
  questionNumber: number;
}) {
  const controls = useDragControls();
  const { courseId } = useParams();
  const useAssessmentStore = createAssessmentStore(courseId as string);
  const { deleteQuestion } = useAssessmentStore();

  // const handleUpdateQuestionTitle = useCallback(
  //   (value: string) => {
  //     updateQuestion(question.id, "question", value);
  //   },
  //   [question.id, updateQuestion]
  // );

  return (
    <Reorder.Item
      id={question.id}
      value={question}
      key={question.id}
      className='bg-neutral-100 rounded-lg p-5 my-2'
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      dragListener={false}
      dragControls={controls}
    >
      <header className='flex justify-between items-center'>
        <div className='flex justify-start gap-3 items-center'>
          <Button
            variant='ghost'
            className='p-2 cursor-grab reorder-handle hover:bg-neutral-200 active:cursor-grabbing'
            onPointerDown={(e) => controls.start(e)}
          >
            <Menu className='size-5' />
          </Button>
          {/* <CustomEditInput
            value={question.question}
            setValue={handleUpdateQuestionTitle}
            textStyle='text-base'
          /> */}

          <h4 className={cn("font- text-base")}>Question {questionNumber}</h4>
        </div>

        <div className='flex items-center gap-2'>
          {/* <Button variant='ghost' onClick={handleAddLecture} className='p-2 hover:bg-neutral-200'>
            <Plus className='size-5' />
          </Button>
          <Button variant='ghost' onClick={handleEditToggle} className='p-2 hover:bg-neutral-200'>
            <PencilLine className='size-5' />
          </Button> */}
          <Button
            variant='ghost'
            className='p-2 hover:bg-neutral-200'
            onClick={() => deleteQuestion(question.id)}
          >
            <Trash2 className='size-5' />
          </Button>
        </div>
      </header>

      <QuestionCard question={question} />
    </Reorder.Item>
  );
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function CustomEditInput({
  value,
  setValue,
  textStyle,
}: {
  value: string;
  setValue: (value: string) => void;
  textStyle?: string;
}) {
  const [isEditing, setIsEditing] = useState(false);

  return (
    <span className='font-bold '>
      {isEditing ? (
        <form
          className='flex items-center gap-2'
          onSubmit={(e) => {
            e.preventDefault();
            setIsEditing(false);
          }}
        >
          <Input
            className='w-full'
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onBlur={(e) => e.target.value.trim() !== "" && setIsEditing(false)}
            autoFocus
          />
          <Button variant='secondary' type='submit' className='py-3 px-4 font-semibold'>
            Save
          </Button>
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
