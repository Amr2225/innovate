import { Button } from "@/components/ui/button";
import { Answer, type MCQQuestion } from "@/types/assessment.type";
import { AnimatePresence, Reorder, motion, useDragControls } from "framer-motion";
import { GripVertical, Info, Plus, Trash } from "lucide-react";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card";
import { useParams } from "next/navigation";
import { createAssessmentStore } from "@/store/assessmentStore";
import { DoubleClickEditInput } from "@/components/doubleClickEditInput";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

export default function MCQQuestion({ question }: { question: MCQQuestion }) {
  const { assessmentId } = useParams();
  const useAssessmentStore = createAssessmentStore(assessmentId as string);
  const { addMCQAnswer, setMCQAnswer, updateQuestion } = useAssessmentStore();

  return (
    <div>
      <span className='flex justify-start items-center gap-1.5 mb-2'>
        <h3 className='text-base font-[500]'>Enter Answers</h3>
        <HoverCard>
          <HoverCardTrigger asChild className='cursor-pointer hover:text-primary'>
            <Info className='size-3.5 text-neutral-500' />
          </HoverCardTrigger>
          <HoverCardContent className='w-fit'>
            <p className='text-[13px] text-neutral-600'>To change the answer double click on it</p>
          </HoverCardContent>
        </HoverCard>
      </span>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.2 }}
      >
        <Reorder.Group
          values={question.options || []}
          onReorder={(newOrder) => setMCQAnswer(question.id, newOrder)}
          //   initial={{ opacity: 0, y: 10 }}
          //   animate={{ opacity: 1, y: 0 }}
          //   exit={{ opacity: 0, y: -10 }}
          //   transition={{ duration: 0.2 }}
          //   layoutId={`mcq-${question.id}`}
        >
          <div className='flex gap-2 items-start'>
            <div className='flex-1'>
              <AnimatePresence>
                {question.options?.map((answer) => (
                  <AnswerItem key={answer.id} questionId={question.id} answer={answer} />
                ))}
              </AnimatePresence>
              <Button
                variant='link'
                className='pl-0 text-xs text-neutral-500 hover:text-neutral-600'
                type='button'
                onClick={() => addMCQAnswer(question.id)}
              >
                <Plus className='size-3' />
                Add Answer
              </Button>
            </div>

            <div className='flex-[0.25]'>
              <div>
                <Label className='mb-1 block'>Correct Answer</Label>
                <Input
                  value={question.correctOption || ""}
                  type='text'
                  placeholder='Correct Answer'
                  onChange={(e) =>
                    updateQuestion<MCQQuestion>(question.id, "correctOption", e.target.value)
                  }
                  onBlur={() => {
                    if (
                      !question.options
                        .map((option) => option.option)
                        .includes(question.correctOption)
                    ) {
                      toast.error("Correct answer is not in the options");
                      updateQuestion<MCQQuestion>(question.id, "correctOption", "");
                    }
                  }}
                />

                <Label className='mt-3 mb-1 block'>Grade</Label>
                <Input
                  value={question.totalGrade || ""}
                  type='number'
                  placeholder='Grade'
                  onChange={(e) =>
                    updateQuestion<MCQQuestion>(question.id, "totalGrade", e.target.value)
                  }
                />
              </div>
            </div>
          </div>
        </Reorder.Group>
      </motion.div>
    </div>
  );
}

function AnswerItem({ questionId, answer }: { questionId: string; answer: Answer }) {
  const { assessmentId } = useParams();
  const useAssessmentStore = createAssessmentStore(assessmentId as string);
  const { deleteMCQAnswer, updateMCQAnswer } = useAssessmentStore();

  const controls = useDragControls();

  return (
    <Reorder.Item
      id={answer.id}
      value={answer}
      dragControls={controls}
      dragListener={false}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3 }}
      layout
      layoutId={answer.id}
    >
      <div className='bg-white flex items-center min-w-[50%] w-fit pb-1 gap-2 border-b border-primary mt-1 justify-between'>
        <div className='flex items-center justify-center gap-1'>
          <Button
            variant='ghost'
            className='hover:text-primary px-1 cursor-grab active:cursor-grabbing'
            onPointerDown={(e) => controls.start(e)}
          >
            <GripVertical className='!size-[18px]' />
          </Button>
          {/* <h6 className='text-sm'>{answer.option}</h6> */}

          <DoubleClickEditInput
            textStyle='text-sm font-normal'
            value={answer.option}
            setValue={(value) => updateMCQAnswer(questionId, answer.id, "option", value)}
          />
        </div>

        <div className='flex items-center gap-2'>
          <Button
            variant='ghost'
            size='icon'
            className='hover:text-red-500'
            onClick={() => deleteMCQAnswer(questionId, answer.id)}
          >
            <Trash className='size-3' />
          </Button>
        </div>
      </div>
    </Reorder.Item>
  );
}
