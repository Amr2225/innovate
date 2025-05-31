import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAssessmentStore } from "@/store/assessmentStore";
import { Question } from "@/types/assessment.type";

export default function HandWrittenQuestion({ question }: { question: Question }) {
  const { updateQuestion } = useAssessmentStore();

  return (
    <div>
      <Label>Answer Key (Optional)</Label>
      <Input
        value={question.handWrittenAnswerKey || ""}
        onChange={(e) => updateQuestion(question.id, "handWrittenAnswerKey", e.target.value)}
        type='text'
        placeholder='Answer Key'
      />
    </div>
  );
}
