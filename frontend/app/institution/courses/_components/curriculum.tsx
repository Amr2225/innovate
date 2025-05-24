import React, { useCallback, useState } from "react";

// Components
import { Button } from "@/components/ui/button";
import ChapterCard from "./curriculum/chapter";

// API
import { useMutation } from "@tanstack/react-query";
import { CreateLectureService, createChapterService } from "@/apiService/courseService";

// Types
import { CreateLecture, CreateChapter } from "@/types/course.type";

// Animation
import { closestCenter, DndContext, DragEndEvent, MouseSensor, useSensor } from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { motion, Reorder } from "framer-motion";

// Store
import { useCourseStore } from "@/store/courseStore";

// Icons
import { Plus } from "lucide-react";

export default function Curriculum() {
  const [chapterId, setChapterId] = useState<string | null>(null);

  const { chapters, setChapters, addChapter, updateChapter, addLecture } = useCourseStore();

  const mouseSensors = useSensor(MouseSensor, {
    activationConstraint: {
      distance: 5,
      tolerance: 5,
      delay: 0,
    },
  });

  const handleDragEnd = useCallback(
    (e: DragEndEvent) => {
      const { active, over } = e;

      if (!over) return;
      if (!over.data.current?.allowedDraggables?.includes(active.data.current?.type as string))
        return;

      const lectureId = active.id as string;
      const chapterId = active.data.current?.chapterId as string;
      const newChapterId = over.id as string;

      if (chapterId === newChapterId) return;

      const activeChapter = chapters.find((chapter) => chapter.id === chapterId);
      if (!activeChapter) return chapters;

      const activeLecture = activeChapter.lectures.find((lecture) => lecture.id === lectureId);
      if (!activeLecture) return chapters;

      const updatedChapters = chapters.map((chapter) => {
        if (chapter.id === chapterId) {
          return {
            ...chapter,
            lectures: chapter.lectures.filter((lecture) => lecture.id !== lectureId),
          };
        }
        if (chapter.id === newChapterId) {
          return {
            ...chapter,
            lectures: [...chapter.lectures, activeLecture],
          };
        }
        return chapter;
      });

      setChapters(updatedChapters);
    },
    [chapters, setChapters]
  );

  const { mutate: createChapter } = useMutation({
    mutationFn: (chapter: CreateChapter) => createChapterService(chapter),
    onSuccess: (data) => {
      console.log("chapterData", data);
      setChapterId(data.id);
    },
    onError: (error) => {
      console.log(error);
    },
  });

  const { mutate: createLecture } = useMutation({
    mutationFn: (lecture: CreateLecture) => CreateLectureService(lecture),
    onError: (error) => {
      console.log(error);
    },
  });

  const handleCreation = () => {
    const cousrseId = "b1a396ca-4731-4adc-a764-28912c6be63b";
    createChapter({
      title: chapters[chapters.length - 1].title,
      course: cousrseId,
    });

    if (chapterId)
      createLecture({
        title: chapters[chapters.length - 1].lectures[0].title,
        description: chapters[chapters.length - 1].lectures[0].description,
        video: null,
        videoPreview: null,
        attachments: null,
        chapter: chapterId,
      });
  };

  return (
    <DndContext
      onDragEnd={handleDragEnd}
      collisionDetection={closestCenter}
      sensors={[mouseSensors]}
    >
      <SortableContext items={chapters} strategy={verticalListSortingStrategy}>
        <motion.section className='h-full w-full' layout>
          <Reorder.Group axis='y' values={chapters} onReorder={(chapters) => setChapters(chapters)}>
            {chapters.map((chapter, index) => (
              <ChapterCard
                key={chapter.id}
                chapter={chapter}
                chapterLength={chapters.length}
                index={index}
                updateChapter={updateChapter}
                addLecture={addLecture}
              />
            ))}
          </Reorder.Group>

          <Button
            variant='secondary'
            className='w-full py-5 font-semibold mt-2'
            onClick={addChapter}
          >
            <Plus className='size-5 mr-1' />
            Add Chapter
          </Button>

          <Button type='button' onClick={handleCreation}>
            Submit
          </Button>
        </motion.section>
      </SortableContext>
    </DndContext>
  );
}
