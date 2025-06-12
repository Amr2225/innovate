import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { createSolveAssessmentStore } from "@/store/solveAssessmentStore";

interface MCQQuestionProps {
  assessmentId: string;
  question: string;
  questionId: string;
  options: string[];
}

export default function MCQQuestion({
  assessmentId,
  questionId,
  question,
  options,
}: MCQQuestionProps) {
  const useSolveAssessmentStore = createSolveAssessmentStore(assessmentId);
  const { mcqAnswers, setMcqAnswer } = useSolveAssessmentStore();

  return (
    <div className='p-5 pt-2.5 mb-1'>
      <h1 className='text-lg font-semibold mb-2'>{question}</h1>
      <div className='pl-3'>
        <RadioGroup
          onValueChange={(value) => setMcqAnswer(questionId, value)}
          value={mcqAnswers[questionId] || ""}
        >
          {options.map((option, index) => (
            <div key={index} className='flex items-center gap-3'>
              <RadioGroupItem value={option} id={`${option}-${index}`} />
              <Label htmlFor={`${option}-${index}`} className='text-base cursor-pointer'>
                {option}
              </Label>
            </div>
          ))}
        </RadioGroup>
      </div>
    </div>
  );
}
