import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createAssessmentStore } from "@/store/assessmentStore";
import { type HandWrittenQuestion } from "@/types/assessment.type";
import { useParams } from "next/navigation";

export default function HandWrittenQuestion({ question }: { question: HandWrittenQuestion }) {
  const { assessmentId } = useParams();
  const useAssessmentStore = createAssessmentStore(assessmentId as string);
  const { updateQuestion } = useAssessmentStore();

  return (
    <div>
      <Label>Answer Key (Optional)</Label>
      <Input
        value={question.handWrittenAnswerKey || ""}
        onChange={(e) =>
          updateQuestion<HandWrittenQuestion>(question.id, "handWrittenAnswerKey", e.target.value)
        }
        type='text'
        placeholder='Answer Key'
      />

      <Label className='mt-3 mb-1 block'>Grade</Label>
      <Input
        value={question.totalGrade || ""}
        onChange={(e) =>
          updateQuestion<HandWrittenQuestion>(question.id, "totalGrade", e.target.value)
        }
        type='number'
        placeholder='Grade'
      />
    </div>
  );
}
