import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { createAssessmentStore } from "@/store/assessmentStore";
import { Question } from "@/types/assessment.type";
import { Reorder, useDragControls } from "framer-motion";
import { Menu, Trash2 } from "lucide-react";
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
  const { asssssmentmentId } = useParams();
  const useAssessmentStore = createAssessmentStore(asssssmentmentId as string);
  const { deleteQuestion } = useAssessmentStore();

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

          <h4 className={cn("font- text-base")}>Question {questionNumber}</h4>
        </div>

        <div className='flex items-center gap-2'>
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
