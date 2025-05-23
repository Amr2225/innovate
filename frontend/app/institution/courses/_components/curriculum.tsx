import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";

// Components
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import EditInput from "./editInput";
import { DialogClose } from "@/components/ui/dialog";

import { useDropzone } from "react-dropzone";

// Icons
import { Menu, PencilLine, Plus, Trash2, Video } from "lucide-react";
import CustomDialog from "./CustomDialog";

// API
import { useMutation } from "@tanstack/react-query";
import { CreateLectureService, createChapterService } from "@/apiService/courseService";
import { CreateLecture, CreateChapter, Chapter, Lecture } from "@/types/course.type";
import { cn } from "@/lib/utils";

import Player from "next-video/player";
import {
  closestCenter,
  DndContext,
  DragEndEvent,
  MouseSensor,
  useDndMonitor,
  useDraggable,
  useDroppable,
  useSensor,
} from "@dnd-kit/core";
import { CSS } from "@dnd-kit/utilities";

import { SortableContext, useSortable, verticalListSortingStrategy } from "@dnd-kit/sortable";

import { motion, Reorder, useDragControls } from "framer-motion";
// import awesomeVideo from "@/videos/get-started.mp4.json";

import { useCourseStore } from "@/store/courseStore";
import { getVideo } from "@/store/videoStorage";

interface LecturesProps {
  chapterId: string;
  lectures: Lecture[];

  draggedItem: Lecture | null;
  setDraggedItem: (item: Lecture | null) => void;
  overChapter: string | null;
  setOverChapter: (chapterId: string | null) => void;
}

interface ChapterCardProps {
  chapter: Chapter;
  chapterLength: number;
  index: number;

  draggedItem: Lecture | null;
  setDraggedItem: (item: Lecture | null) => void;
  overChapter: string | null;
  setOverChapter: (chapterId: string | null) => void;

  updateChapter: (chapterId: string, key: string, value: string) => void;
  addLecture: (chapterId: string) => void;
}

interface LectureItemProps {
  lecture: Lecture;
  index: number;
  chapterId: string;
  lectureLength: number;
}

const ChapterCard = React.memo(
  ({
    chapter,
    chapterLength,
    index,
    updateChapter,
    addLecture,
    overChapter,
    draggedItem,
    setDraggedItem,
    setOverChapter,
  }: ChapterCardProps) => {
    const [isEditing, setIsEditing] = useState<boolean[]>([]);
    const [isActive, setIsActive] = useState<boolean>(false);
    const [, setTopIndicatorActive] = useState<boolean>(false);

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

    const chapterDraggable = useDraggable({
      id: chapter.id,
      data: {
        type: "chapter",
        chapterId: chapter.id,
      },
    });

    useDndMonitor({
      onDragMove(event) {
        const type = event.active.data.current?.type;
        if (type === "lecture") {
          setIsActive(true);
        }
        if (type === "chapter") {
          //TODO:change this to a generic topIndicator
          setTopIndicatorActive(true);
        }
      },
      onDragEnd() {
        setIsActive(false);
        setTopIndicatorActive(false);
      },
    });

    const handleDragOver = () => {};

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

    // 3. Combine the refs
    const setRefs = useCallback(
      (node: HTMLElement | null) => {
        chapterDroppable.setNodeRef(node);
        chapterDraggable.setNodeRef(node);
      },
      [chapterDraggable, chapterDroppable]
    );

    const controls = useDragControls();

    return (
      <div onMouseEnter={() => draggedItem && setOverChapter(chapter.title)}>
        <Reorder.Item
          className='chapter'
          value={chapter}
          id={chapter.id}
          dragListener={false}
          dragControls={controls}
          as='div'
        >
          <motion.div
            className={cn("bg-neutral-100 rounded-lg p-5 my-2", {
              "border border-primary": chapterDroppable.isOver && isActive,
              // "z-[1]": !isActive,
              // "z-[2]": isActive,
            })}
            ref={setRefs}
            layout
            onDragOver={handleDragOver}
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
            <LecturesCard
              chapterId={chapter.id}
              lectures={chapter.lectures}
              draggedItem={draggedItem}
              setDraggedItem={setDraggedItem}
              overChapter={overChapter}
              setOverChapter={setOverChapter}
            />
          </motion.div>
        </Reorder.Item>
      </div>
    );
  }
);

ChapterCard.displayName = "ChapterCard";

const LectureItem = React.memo(({ lecture, index, chapterId, lectureLength }: LectureItemProps) => {
  const [isEditing, setIsEditing] = useState<boolean[]>([]);
  const [dialogOpen, setDialogOpen] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const { updateLecture, deleteLecture } = useCourseStore();

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 1) {
        return;
      }
      updateLecture(chapterId, lecture.id, "video", acceptedFiles[0]);
    },
    [chapterId, lecture.id, updateLecture]
  );

  useEffect(() => {
    setIsEditing(new Array(lectureLength).fill(false));
  }, [lectureLength]);

  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: lecture.id,
    data: {
      type: "lecture",
      chapterId,
      lectureId: lecture.id,
    },
  });

  const style = useMemo(
    () =>
      transform
        ? {
            // transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
            transform: CSS.Transform.toString(transform),
            transition,
            // zIndex: 9999,
            // position: "relative" as const,
            // pointerEvents: "none" as const,
          }
        : undefined,
    [transform, transition]
  );

  const handleEditToggle = useCallback(() => {
    setIsEditing((prev) => {
      const newIsEditing = [...prev];
      newIsEditing[index] = !newIsEditing[index];
      return newIsEditing;
    });
  }, [index, setIsEditing]);

  const handleEditClose = useCallback(() => {
    setIsEditing((prev) => {
      const newIsEditing = [...prev];
      newIsEditing[index] = false;
      return newIsEditing;
    });
  }, [index, setIsEditing]);

  const handleUpdateLecture = useCallback(
    (value: string) => {
      updateLecture(chapterId, lecture.id, "title", value);
    },
    [chapterId, lecture.id, updateLecture]
  );

  const handleDeleteLecture = useCallback(() => {
    deleteLecture(chapterId, lecture.id);
  }, [chapterId, lecture.id, deleteLecture]);

  const handleSetDialogOpen = useCallback(
    (value: string) => {
      setDialogOpen(value);
    },
    [setDialogOpen]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  // Load video from IndexedDB when needed
  useEffect(() => {
    const loadVideo = async () => {
      if (lecture.video?.storageKey) {
        const video = await getVideo(lecture.video.storageKey);
        if (video) {
          const url = URL.createObjectURL(video);
          setPreviewUrl(url);
          return () => URL.revokeObjectURL(url);
        }
      }
    };
    loadVideo();
  }, [lecture.video?.storageKey]);

  return (
    <div
      // ref={setNodeRef}
      style={style}
      draggable={true}
      className={cn(
        "flex justify-between gap-3 items-center bg-white p-5 text-neutral-600",
        {
          "border border-primary shadow-lg": isDragging,
        },
        isDragging ? "!z-[9999]" : "!z-0"
      )}
    >
      <div className='flex justify-start gap-3 items-center'>
        <Button
          variant='ghost'
          className='p-2 cursor-grab active:cursor-grabbing'
          {...attributes}
          {...listeners}
        >
          <Menu className='size-5' />
        </Button>
        <EditInput
          isEditing={isEditing[index]}
          closeEditing={handleEditClose}
          value={lecture.title}
          setValue={handleUpdateLecture}
        />
      </div>

      <div className='flex items-center gap-2'>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant='secondary' className='py-3 px-4 font-semibold'>
              Contents
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className='hover:[&>div]:cursor-pointer'>
            <DropdownMenuItem onClick={() => handleSetDialogOpen("video")}>Video</DropdownMenuItem>
            <DropdownMenuItem>Attach File</DropdownMenuItem>
            <DropdownMenuItem>Captions</DropdownMenuItem>
            <DropdownMenuItem>Description</DropdownMenuItem>
            <DropdownMenuItem>Lecture Notes</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <Button variant='ghost' onClick={handleEditToggle} className='p-2 hover:bg-neutral-200'>
          <PencilLine className='size-5' />
        </Button>

        <Button
          variant='ghost'
          onClick={handleDeleteLecture}
          className='p-2 hover:bg-neutral-200 group'
        >
          <Trash2 className='size-5 group-hover:text-red-600' />
        </Button>
      </div>

      <CustomDialog
        title='Video'
        description='Upload a video for the lecture'
        open={dialogOpen === "video"}
        setOpen={(open) => setDialogOpen(open ? "video" : null)}
      >
        <div className='flex justify-center items-center h-[250px] w-full rounded-md border border-neutral-300 overflow-hidden'>
          {!lecture.video ? (
            <div
              {...getRootProps()}
              className='flex justify-center items-center w-full h-full flex-col gap-2 cursor-pointer'
            >
              <input {...getInputProps()} accept='video/*' />
              <Video
                className={cn("size-10 text-neutral-400", {
                  "text-primary": isDragActive,
                })}
              />
              <p className={cn("text-neutral-400", { "text-primary": isDragActive })}>
                No video selected
              </p>
            </div>
          ) : (
            <div className='w-full h-full'>
              <Player src={previewUrl as string} />
            </div>
          )}
        </div>
        <div className='flex justify-between items-center gap-2'>
          <div className='space-x-2'>
            <DialogClose asChild>
              <Button type='button' variant='secondary'>
                Close
              </Button>
            </DialogClose>
            {lecture.video && (
              <Button
                variant='link'
                onClick={() => updateLecture(chapterId, lecture.id, "video", null)}
              >
                Reset
              </Button>
            )}
          </div>
          <Button>Upload</Button>
        </div>
      </CustomDialog>
    </div>
  );
});

LectureItem.displayName = "LectureItem";

export default function Curriculum() {
  // const [chapters, setChapters] = useState<CustomChapter[]>([]);
  const [chapterId, setChapterId] = useState<string | null>(null);
  const [draggedItem, setDraggedItem] = useState<Lecture | null>(null);
  const [overChapter, setOverChapter] = useState<string | null>(null);

  const { chapters, setChapters, addChapter, updateChapter, addLecture } = useCourseStore();

  const mouseSensors = useSensor(MouseSensor, {
    activationConstraint: {
      distance: 0,
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

      if (active.data.current?.type === "chapter") {
        const oldChapterId = over.data.current?.chapterId as string;
        const oldChapterIndex = chapters.findIndex((chapter) => chapter.id === oldChapterId);
        const chapterToMove = chapters.find((chapter) => chapter.id === active.id)!;
        const newChapters = chapters
          .filter((chapter) => chapter.id !== active.id)
          .toSpliced(oldChapterIndex, 0, chapterToMove);

        setChapters(newChapters);
        return;
      }

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
      <SortableContext
        items={chapters.map((chapter) => chapter.id)}
        strategy={verticalListSortingStrategy}
      >
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
                draggedItem={draggedItem}
                setDraggedItem={setDraggedItem}
                overChapter={overChapter}
                setOverChapter={setOverChapter}
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

const LecturesCard = ({ chapterId, lectures }: LecturesProps) => {
  const { setLecture } = useCourseStore();
  return (
    <Reorder.Group
      axis='y'
      values={lectures}
      onReorder={(lecture) => {
        setLecture(chapterId, lecture);
      }}
      className='mt-3 space-y-3'
      as='div'
    >
      {lectures.map((lecture, index) => (
        // <Reorder.Item key={lecture.id} value={lecture}>
        <LectureItem
          key={lecture.id}
          lecture={lecture}
          index={index}
          chapterId={chapterId}
          lectureLength={lectures.length}
        />
        // </Reorder.Item>
      ))}
    </Reorder.Group>
  );
};
