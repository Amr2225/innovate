"use client";
import React, { useCallback, useState } from "react";

// Components
import EditInput from "@/components/editInput";
import { Button } from "@/components/ui/button";

// Utils
import { cn } from "@/lib/utils";

// Types
import { Chapter } from "@/types/course.type";

// Framer Motion
import { Reorder, useDragControls } from "framer-motion";

// Icons
import { Menu, PencilLine, Trash2, Plus } from "lucide-react";

// Components
import LecturesCard from "./lecture";
import { useDroppable } from "@dnd-kit/react";

// Store
import { createCourseStore } from "@/store/courseStore";

// Hooks
import { useParams } from "next/navigation";

interface ChapterCardProps {
  chapter: Chapter;
  index: number;
}

function ChapterCard({ chapter, index }: ChapterCardProps) {
  const { courseId } = useParams();
  const useCourseStore = createCourseStore((courseId as string) || "new");

  const { updateChapter, deleteChapter, addLecture, chapters } = useCourseStore();

  const [isEditing, setIsEditing] = useState<boolean[]>(new Array(chapters.length).fill(false));

  const { ref, isDropTarget } = useDroppable({
    id: chapter.id,
    data: {
      allowedDraggables: ["lecture"],
      chapterId: chapter.id,
    },
  });

  const handleEditToggle = useCallback(() => {
    setIsEditing((prev) => {
      const newIsEditing = [...prev];
      newIsEditing[index] = !newIsEditing[index];
      return newIsEditing;
    });
  }, [index, setIsEditing]);

  const handleCloseEditing = useCallback(() => {
    const newIsEditing = [...isEditing];
    newIsEditing[index] = false;
    setIsEditing(newIsEditing);
  }, [index, isEditing, setIsEditing]);

  const handleUpdateTitle = useCallback(
    (value: string) => {
      updateChapter(chapter.id, "title", value);
    },
    [chapter.id, updateChapter]
  );

  const handleAddLecture = useCallback(() => {
    addLecture(chapter.id);
  }, [chapter.id, addLecture]);

  const controls = useDragControls();

  return (
    <Reorder.Item
      id={chapter.id}
      value={chapter}
      className={cn("bg-neutral-100 rounded-lg p-5 my-2", {
        "border border-primary": isDropTarget,
      })}
      layout
      initial={{ opacity: 0, y: 100 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      dragListener={false}
      dragControls={controls}
      ref={ref}
    >
      <header className='flex justify-between items-center'>
        <div className='flex justify-start gap-3 items-center'>
          <Button
            variant='ghost'
            className='p-2 cursor-grab reorder-handle hover:bg-neutral-200 active:cursor-grabbing'
            onPointerDown={(e) => controls.start(e)}
          >
            <Menu className='size-5' />
          </Button>
          <EditInput
            isEditing={isEditing[index]}
            closeEditing={handleCloseEditing}
            value={chapter.title}
            setValue={handleUpdateTitle}
            textStyle='text-base'
          />
        </div>

        <div className='flex items-center gap-2'>
          <Button variant='ghost' onClick={handleAddLecture} className='p-2 hover:bg-neutral-200'>
            <Plus className='size-5' />
          </Button>
          <Button variant='ghost' onClick={handleEditToggle} className='p-2 hover:bg-neutral-200'>
            <PencilLine className='size-5' />
          </Button>
          <Button
            variant='ghost'
            className='p-2 hover:bg-neutral-200'
            onClick={() => deleteChapter(chapter.id)}
          >
            <Trash2 className='size-5' />
          </Button>
        </div>
      </header>
      <LecturesCard chapterId={chapter.id} lectures={chapter.lectures} />
    </Reorder.Item>
  );
}

export default ChapterCard;
