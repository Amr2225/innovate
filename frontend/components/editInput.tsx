"use client";
import React, { useRef } from "react";

// Components
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

type EditInputProps = {
  isEditing: boolean;
  closeEditing: () => void;
  value: string;
  setValue: (value: string) => void;
  textStyle?: string;
};

function EditInput({ isEditing, closeEditing, value, setValue, textStyle }: EditInputProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    if (e.target.value.trim() === "") return;

    setValue(e.target.value);
    closeEditing();
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const inputValue = inputRef.current?.value;
    if (!inputValue) return;
    if (inputValue.trim() === "") return;

    setValue(inputValue);
    closeEditing();
  };

  return (
    <span className='font-bold '>
      {isEditing ? (
        <form className='flex items-center gap-2' onSubmit={handleSubmit}>
          <Input
            ref={inputRef}
            className='w-full'
            defaultValue={value}
            onBlur={handleBlur}
            autoFocus
          />
          <Button variant='secondary' type='submit' className='py-3 px-4 font-semibold'>
            Save
          </Button>
        </form>
      ) : (
        <h4 className={cn("font-bold text-sm", textStyle)}>{value}</h4>
      )}
    </span>
  );
}

export default React.memo(EditInput);
