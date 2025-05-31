import React from "react";

// Components
import { Button } from "@/components/ui/button";
import ChapterCard from "./curriculum/chapter";

// DnD Kit
import { DragDropProvider } from "@dnd-kit/react";
import { motion, Reorder } from "framer-motion";

// Store
import { useCourseStore } from "@/store/courseStore";

// Icons
import { Plus } from "lucide-react";

import { arrayMove } from "@dnd-kit/sortable";

type UniqueIdentifier = string | number;

interface DraggableDroppable {
  id: UniqueIdentifier;
  data?: {
    current?: {
      type?: string;
      chapterId?: string;
    };
  };
}

export default function Curriculum() {
  const { chapters, setChapters, addChapter } = useCourseStore();

  const getContainerId = (id: string) => {
    if (chapters.some((chapter) => chapter.id === id)) {
      return id;
    }

    const chapter = chapters.find((chapter) =>
      chapter.lectures.some((lecture) => lecture.id === id)
    );
    if (!chapter) return null;
    return chapter.id;
  };

  const handleDragOver = (source: DraggableDroppable | null, target: DraggableDroppable | null) => {
    if (!target) return;
    const overId = target.id as string;
    const activeId = source?.id as string;

    const activecontainerid = getContainerId(activeId);
    const overcontainerid = getContainerId(overId);

    if (activecontainerid === overcontainerid) return;

    setChapters((prev) => {
      const activechapter = prev.find((chapter) => chapter.id === activecontainerid);

      if (!activechapter) return prev;

      const activelecture = activechapter.lectures.find((lecture) => lecture.id === activeId);

      if (!activelecture) return prev;

      const newchapters = prev.map((chapter) => {
        if (chapter.id === activecontainerid) {
          return {
            ...chapter,
            lectures: chapter.lectures.filter((lecture) => lecture.id !== activeId),
          };
        }
        if (chapter.id === overcontainerid) {
          return {
            ...chapter,
            lectures: [...chapter.lectures, activelecture],
          };
        }

        const overitemindex = chapter.lectures.findIndex((lecture) => lecture.id === overId);

        if (overitemindex === -1) return chapter;

        return {
          ...chapter,
          lectures: [
            ...chapter.lectures.slice(0, overitemindex + 1),
            activelecture,
            ...chapter.lectures.slice(overitemindex + 1),
          ],
        };
      });

      return newchapters;
    });
  };

  const handleDragEnd = (source: DraggableDroppable | null, target: DraggableDroppable | null) => {
    if (!target) return;
    const activeId = source?.id as string;
    const overId = target.id as string;

    const activeContainerId = getContainerId(activeId);
    const overContainerId = getContainerId(overId);

    if (!activeContainerId || !overContainerId) return;

    if (activeContainerId === overContainerId && source?.id !== target.id) {
      const chapterIndex = chapters.findIndex((chapter) => chapter.id === activeContainerId);
      if (chapterIndex === -1) return;

      const chapter = chapters[chapterIndex];
      const activeIndex = chapter.lectures.findIndex((lecture) => lecture.id === activeId);

      const overIndex = chapter.lectures.findIndex((lecture) => lecture.id === overId);

      if (activeIndex === -1 || overIndex === -1) return;

      setChapters((prev) => {
        return prev.map((currentChapter, index) => {
          if (index === chapterIndex) {
            return {
              ...currentChapter,
              lectures: arrayMove(chapter.lectures, activeIndex, overIndex),
            };
          }
          return currentChapter;
        });
      });
    }
  };

  return (
    <DragDropProvider
      onDragOver={(event) => {
        const { source, target } = event.operation;
        handleDragOver(source, target);
      }}
      onDragEnd={(event) => {
        const { source, target } = event.operation;
        handleDragEnd(source, target);
      }}
    >
      <motion.section className='h-full w-full' layout>
        <Reorder.Group axis='y' values={chapters} onReorder={(chapters) => setChapters(chapters)}>
          {chapters.map((chapter, index) => (
            <ChapterCard key={chapter.id} chapter={chapter} index={index} />
          ))}
        </Reorder.Group>

        <Button variant='secondary' className='w-full py-5 font-semibold mt-2' onClick={addChapter}>
          <Plus className='size-5 mr-1' />
          Add Chapter
        </Button>
      </motion.section>
    </DragDropProvider>
  );
}
