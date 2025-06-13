import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { cn } from "@/lib/utils";
import { type MCQQuestionSubmission } from "@/types/assessmentSubmission.type";

export default function MCQQuestionSubmission({
  question_text,
  options,
  student_answer,
  correct_answer,
  score,
  max_score,
}: MCQQuestionSubmission) {
  return (
    <div className='p-5 pt-2.5 mb-2'>
      <span className='flex justify-between items-center'>
        <h1 className='text-lg font-semibold mb-2'>{question_text}</h1>
        <span className='text-lg font-semibold text-primary'>
          {Number(score).toFixed(1)}/{max_score}
        </span>
      </span>
      <div className='pl-3'>
        <RadioGroup value={student_answer}>
          {options.map((option, index) => (
            <div key={index} className='flex items-center gap-3'>
              <RadioGroupItem value={option} id={`${option}-${index}`} />
              <Label
                htmlFor={`${option}-${index}`}
                className={cn(
                  "text-base",
                  correct_answer === option && "text-green-600 font-semibold"
                )}
              >
                {option}
              </Label>
            </div>
          ))}
        </RadioGroup>
      </div>
    </div>
  );
}
