import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";

export default function MCQQuestion({
  question,
  options,
}: {
  question: string;
  options: string[];
}) {
  return (
    <div className='p-5 pt-2.5 mb-1'>
      <h1 className='text-lg font-semibold mb-2'>{question}</h1>
      <div className='pl-3'>
        <RadioGroup defaultValue='comfortable'>
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
