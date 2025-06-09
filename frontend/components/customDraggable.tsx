import React from "react";

// Components
import EditInput from "@/components/editInput";
import { Button } from "@/components/ui/button";

// Utils
import { cn } from "@/lib/utils";
import { useSortable } from "@dnd-kit/react/sortable";

// Icons
import { Menu } from "lucide-react";

type UniqueIdentifier = string | number;

interface CustomDraggableProps {
  children: React.ReactNode;
  className?: string;
  id: UniqueIdentifier;
  index: number;
  type: string;
  accept?: string | string[];
  group: UniqueIdentifier;
  title: string;
  setTitle: (title: string) => void;
  isEditing: boolean;
  handleEditClose: () => void;
  data?: {
    type?: string;
    parentContainerId?: string; // Chapter ID
    currentContainerId?: string; // Lecture ID
  };
}

export default function CustomDraggable({
  children,
  className,
  id,
  index,
  type,
  accept,
  data,
  group,
  title,
  setTitle,
  isEditing,
  handleEditClose,
}: CustomDraggableProps) {
  const { ref, handleRef, isDragging } = useSortable({
    id,
    index,
    data,
    type,
    accept,
    group,
  });

  return (
    <div
      ref={ref}
      className={cn("flex justify-between gap-3 items-center bg-white p-5 text-neutral-600", {
        "border border-primary shadow-lg": isDragging,
        className,
      })}
    >
      <div className='flex justify-start gap-3 items-center'>
        <Button ref={handleRef} variant='ghost' className='p-2 cursor-grab active:cursor-grabbing'>
          <Menu className='size-5' />
        </Button>
        <EditInput
          isEditing={isEditing}
          closeEditing={handleEditClose}
          value={title}
          setValue={setTitle}
        />
      </div>
      {children}
    </div>
  );
}
