import { useParams } from "next/navigation";

// Store
import { createAssessmentStore } from "@/store/assessmentStore";

// Types
import { AIGeneratedMCQQuestion } from "@/types/assessment.type";

// Icons
import { CheckCircle2, Trash2 } from "lucide-react";

// Components
import { Button } from "@/components/ui/button";
import { DoubleClickEditInput } from "@/components/doubleClickEditInput";

export default function AIGeneratedMcqQuestionPreview({
  AIQuestions,
  AIQuestionId,
}: {
  AIQuestions: AIGeneratedMCQQuestion["questions"];
  AIQuestionId: string;
}) {
  const { assessmentId } = useParams();
  const useAssessmentStore = createAssessmentStore(assessmentId as string);
  const { deleteAIGenerateMCQQueston, updateAIGeneratedMCQAnswer, updateAIGeneratedMCQQuestion } =
    useAssessmentStore();

  return (
    <div className='space-y-6 max-h-[75vh] overflow-y-auto p-2'>
      {AIQuestions?.map((question, questionIndex) => (
        <div key={question.question}>
          <div className='flex items-center gap-2'>
            <DoubleClickEditInput
              value={question.question}
              setValue={(value) => updateAIGeneratedMCQQuestion(AIQuestionId, questionIndex, value)}
              textStyle='font-semibod'
              inputStyle='w-[50vw] font-normal'
              Tag='h1'
            />
            <Button
              variant='secondary'
              className='size-6'
              onClick={() => deleteAIGenerateMCQQueston(AIQuestionId, question.question)}
            >
              <Trash2 className='size-5' />
            </Button>
          </div>
          <ul className='pl-2 space-y-1'>
            {question.options.map((option, optionIndex) => (
              <DoubleClickEditInput
                key={option}
                value={option}
                setValue={(value) =>
                  updateAIGeneratedMCQAnswer(AIQuestionId, questionIndex, optionIndex, value)
                }
                textStyle='flex items-center gap-2 before:content-["•"] before:text-primary before:text-xl before:leading-none font-normal'
                inputStyle='w-[50%] font-normal'
                Tag='li'
              />
            ))}
          </ul>
          <div className='mt-2 flex items-center gap-2 text-sm text-muted-foreground'>
            <CheckCircle2 className='size-4 text-green-500' />
            <span>Correct Answer: {question.correct_answer}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
