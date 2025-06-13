import { useState, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface DoubleClickEditInputProps {
  value: string;
  setValue: (value: string) => void;
  textStyle?: string;
  inputStyle?: string;
  Tag?: keyof JSX.IntrinsicElements;
}

export function DoubleClickEditInput({
  value,
  setValue,
  textStyle,
  inputStyle,
  Tag = "h4",
}: DoubleClickEditInputProps) {
  const [isEditing, setIsEditing] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    if (e.target.value.trim() === "") return;

    setValue(e.target.value);
    setIsEditing(false);
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const inputValue = inputRef.current?.value;
    if (!inputValue) return;
    if (inputValue.trim() === "") return;

    setValue(inputValue);
    setIsEditing(false);
  };

  return (
    <span className='font-bold'>
      {isEditing ? (
        <form className='flex items-center gap-2' onSubmit={handleSubmit}>
          <Input
            className={cn("w-full", inputStyle)}
            defaultValue={value}
            ref={inputRef}
            onBlur={handleBlur}
            autoFocus
          />
          <div className='flex items-center gap-2'>
            {/* <Button variant='secondary' type='button' className='px-3 text-xs font-semibold'>
              Cancel
            </Button> */}
            <Button variant='default' type='submit' className='px-3 text-xs font-semibold'>
              Save
            </Button>
          </div>
        </form>
      ) : (
        <Tag
          onDoubleClick={() => setIsEditing(true)}
          className={cn("font-bold text-sm select-none", textStyle)}
        >
          {value}
        </Tag>
      )}
    </span>
  );
}
