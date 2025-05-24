import React, { memo, useCallback, useEffect, useState } from "react";
// Components
import EditInput from "../editInput";

// DnD Kit
import { useDroppable } from "@dnd-kit/core";
import { Button } from "@/components/ui/button";

// Utils
import { cn } from "@/lib/utils";

// Types
import { Chapter } from "@/types/course.type";

// Framer Motion
import { motion, useDragControls } from "framer-motion";
import { Reorder } from "framer-motion";

// Icons
import { Menu, PencilLine, Trash2, Plus } from "lucide-react";

// Components
import LecturesCard from "./lecture";

interface ChapterCardProps {
  chapter: Chapter;
  chapterLength: number;
  index: number;

  updateChapter: (chapterId: string, key: string, value: string) => void;
  addLecture: (chapterId: string) => void;
}

function ChapterCard({
  chapter,
  chapterLength,
  index,
  updateChapter,
  addLecture,
}: ChapterCardProps) {
  const [isEditing, setIsEditing] = useState<boolean[]>([]);

  useEffect(() => {
    setIsEditing(new Array(chapterLength).fill(false));
  }, [chapterLength]);

  const chapterDroppable = useDroppable({
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
    <div data-column={chapter.id}>
      <Reorder.Item
        className='chapter'
        value={chapter}
        id={chapter.id}
        dragListener={false}
        dragControls={controls}
        onDragOver={() => console.log("drag over")}
        as='div'
      >
        <motion.div
          className={cn("bg-neutral-100 rounded-lg p-5 my-2", {
            "border border-primary": chapterDroppable.isOver,
            // "z-[1]": !isActive,
            // "z-[2]": isActive,
          })}
          ref={chapterDroppable.setNodeRef}
          layout
          initial={{ opacity: 0, y: 100 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
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
              <Button
                variant='ghost'
                onClick={handleAddLecture}
                className='p-2 hover:bg-neutral-200'
              >
                <Plus className='size-5' />
              </Button>
              <Button
                variant='ghost'
                onClick={handleEditToggle}
                className='p-2 hover:bg-neutral-200'
              >
                <PencilLine className='size-5' />
              </Button>
              <Button variant='ghost' className='p-2 hover:bg-neutral-200'>
                <Trash2 className='size-5' />
              </Button>
            </div>
          </header>
          <LecturesCard chapterId={chapter.id} lectures={chapter.lectures} />
        </motion.div>
      </Reorder.Item>
    </div>
  );
}

export default memo(ChapterCard);
