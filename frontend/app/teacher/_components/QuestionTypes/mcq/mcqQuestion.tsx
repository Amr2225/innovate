import { Button } from "@/components/ui/button";
import { useAssessmentStore } from "@/store/assessmentStore";
import { Answer, Question } from "@/types/assessment.type";
import { AnimatePresence, Reorder, motion, useDragControls } from "framer-motion";
import { GripVertical, Info, Plus, Trash } from "lucide-react";
import { CustomEditInput } from "../../questionCard";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card";

export default function MCQQuestion({ question }: { question: Question }) {
  const { addMCQAnswer, setMCQAnswer } = useAssessmentStore();

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
        </Reorder.Group>
      </motion.div>
    </div>
  );
}

function AnswerItem({ questionId, answer }: { questionId: string; answer: Answer }) {
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

          <CustomEditInput
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
