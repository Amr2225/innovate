import React from "react";

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
  return (
    <span className='font-bold '>
      {isEditing ? (
        <form
          className='flex items-center gap-2'
          onSubmit={(e) => {
            e.preventDefault();
            closeEditing();
          }}
        >
          <Input className='w-full' value={value} onChange={(e) => setValue(e.target.value)} />
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
