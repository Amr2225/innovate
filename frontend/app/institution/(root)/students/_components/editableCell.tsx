import { useState, useRef, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";
import { Save } from "lucide-react";
import moment from "moment";
import { BirthDatePicker } from "@/components/date-picker";
import { cn } from "@/lib/utils";

export default function EditableCellContent({
  userId,
  value,
  field,
  isEditable = true,
  onSave,
}: {
  userId: string;
  value: string | number | boolean;
  field: string;
  isEditable?: boolean;
  onSave: (userId: string, field: string, value: string | number | boolean | Date) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [inputValue, setInputValue] = useState(
    typeof value === "string" && moment(value).isValid() ? moment(value).toDate() : String(value)
  );
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input when entering edit mode
  useEffect(() => {
    if (editing && inputRef.current) {
      inputRef.current.focus();
    }
  }, [editing]);

  // Handle double-click to enter edit mode
  const handleDoubleClick = () => {
    setEditing(true);
    setInputValue(String(value));
  };

  // Save changes
  const handleSave = () => {
    setEditing(false);
    if (inputValue !== String(value)) {
      onSave(userId, field, inputValue);
    }
  };

  // Cancel edit
  const handleCancel = () => {
    setEditing(false);
    setInputValue(String(value));
  };

  // Handle keyboard events
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSave();
    } else if (e.key === "Escape") {
      handleCancel();
    }
  };

  // Handle input change
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    if (e.relatedTarget?.id !== "save" && e.relatedTarget?.id !== "cancel") {
      handleCancel();
    }
  };

  // Render edit mode
  if (editing) {
    return (
      <div className='flex items-center gap-1'>
        <Input
          ref={inputRef}
          value={inputValue as string}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          className='h-8 px-2 py-1 text-sm'
          autoFocus
        />
        <div className='flex gap-1'>
          <Button
            variant='ghost'
            size='icon'
            className='h-6 w-6'
            type='button'
            id='save'
            onClick={handleSave}
          >
            <Save className='h-3 w-3' />
          </Button>
          <Button
            variant='ghost'
            size='icon'
            className='h-6 w-6'
            type='button'
            id='cancel'
            onClick={handleCancel}
          >
            <X className='h-3 w-3' />
          </Button>
        </div>
      </div>
    );
  }

  if (typeof value === "boolean") {
    return (
      <div>
        <span
          className={cn(
            "px-2 py-1 rounded-full text-xs font-medium",
            value ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
          )}
        >
          {value ? "Yes" : "No"}
        </span>
      </div>
    );
  }

  if (typeof value === "string" && moment(value).isValid()) {
    if (isEditable) {
      return (
        <BirthDatePicker
          date={inputValue as Date}
          setDate={(date) => setInputValue(date as Date)}
          saveButton={
            <Button variant='link' className='w-full' onClick={handleSave}>
              Save
            </Button>
          }
        />
      );
    }
    return <p className='text-[13px]'>{moment(value).format("DD/MM/YYYY")}</p>;
  }

  // Render display mode
  return (
    <p
      onDoubleClick={handleDoubleClick}
      className='cursor-pointer hover:bg-muted/50 py-1 rounded text-[13px]'
      title='Double-click to edit'
    >
      {value}
    </p>
  );
}
