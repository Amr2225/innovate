import { memo, useCallback, useEffect, useMemo, useState } from "react";
import { useDropzone } from "react-dropzone";
import { cn } from "@/lib/utils";

// Components
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import CustomDialog from "../CustomDialog";
import EditInput from "../editInput";
import { Button } from "@/components/ui/button";

// DnD
import { CSS } from "@dnd-kit/utilities";
import { Menu, PencilLine, Trash2 } from "lucide-react";
import { DialogClose } from "@/components/ui/dialog";
import { Lecture, Chapter } from "@/types/course.type";
import { useSortable } from "@dnd-kit/sortable";

// Store
import { useCourseStore } from "@/store/courseStore";
import { getVideo } from "@/store/videoStorage";

// Icons
import { Video } from "lucide-react";

// Video Player
import Player from "next-video/player";

// Framer Motion
import { PanInfo, Reorder, useDragControls } from "framer-motion";

interface LectureItemProps {
  lecture: Lecture;
  index: number;
  chapterId: string;
  lectureLength: number;
}

interface LecturesProps {
  chapterId: string;
  lectures: Lecture[];
}

function LectureItem({ lecture, index, chapterId, lectureLength }: LectureItemProps) {
  const [isEditing, setIsEditing] = useState<boolean[]>([]);
  const [dialogOpen, setDialogOpen] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const { updateLecture, deleteLecture, setChapters, chapters } = useCourseStore();

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

  const dragControls = useDragControls();

  const handleDragEnd = (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    setTimeout(() => {
      const dropZone = document.elementFromPoint(info.point.x, info.point.y);
      const chapter = dropZone?.closest("[data-column]");

      if (!chapter) return;

      const newChapterId = chapter.getAttribute("data-column");
      console.log("New chapterId", chapterId);

      const newChapters = chapters.map((chapter) => {
        if (chapter.id === chapterId) {
          return {
            ...chapter,
            lectures: chapter.lectures.filter((lecture) => lecture.id !== lecture.id),
          };
        }
        if (chapter.id === newChapterId) {
          return {
            ...chapter,
            lectures: [...chapter.lectures, lecture],
          };
        }
        return chapter;
      });

      setChapters(newChapters);

      // const targetColumn = columnElement.getAttribute("data-column");
      // const sourceColumn = item.status;

      // if (targetColumn === sourceColumn) return;
    }, 100);
  };

  return (
    <Reorder.Item
      key={lecture.id}
      value={lecture}
      dragConstraints={false}
      dragElastic={0.1}
      dragControls={dragControls}
      dragListener={false}
      // onDragEnd={(event, info) => handleDragEnd(event, info)}
      style={style}
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
          //   {...attributes}
          //   {...listeners}
          onPointerDown={(e) => dragControls.start(e)}
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
    </Reorder.Item>
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
        <LectureItem
          key={lecture.id}
          lecture={lecture}
          index={index}
          chapterId={chapterId}
          lectureLength={lectures.length}
        />
      ))}
    </Reorder.Group>
  );
};

export default memo(LecturesCard);
