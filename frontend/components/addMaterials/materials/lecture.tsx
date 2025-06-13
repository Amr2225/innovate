"use client";
import { useCallback, useState } from "react";

// Components
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

// DnD
import { PencilLine, Trash2 } from "lucide-react";
import { Lecture } from "@/types/course.type";

// Store
import { createCourseStore } from "@/store/courseStore";

// Video Player
import CustomDraggable from "@/components/customDraggable";
import DialogGroup from "./dialogGroup";

// Hooks
import { useParams } from "next/navigation";

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
  const [isEditing, setIsEditing] = useState<boolean[]>(new Array(lectureLength).fill(false));
  const [dialogOpen, setDialogOpen] = useState<string | null>(null);

  const { courseId } = useParams();
  const useCourseStore = createCourseStore((courseId as string) || "new");
  const { updateLecture, deleteLecture } = useCourseStore();

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

  return (
    <CustomDraggable
      id={lecture.id}
      index={index}
      type='lecture'
      accept='lecture'
      group={chapterId}
      title={lecture.title}
      setTitle={handleUpdateLecture}
      isEditing={isEditing[index]}
      handleEditClose={handleEditClose}
    >
      <div className='flex items-center gap-2'>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant='secondary' className='py-3 px-4 font-semibold'>
              Contents
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className='hover:[&>div]:cursor-pointer'>
            <DropdownMenuItem onClick={() => setDialogOpen("video")}>Video</DropdownMenuItem>
            <DropdownMenuItem onClick={() => setDialogOpen("description")}>
              Description
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setDialogOpen("attachment")}>
              Attach File
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <Button variant='ghost' onClick={handleEditToggle} className='p-2 hover:bg-neutral-200'>
          <PencilLine className='size-5' />
        </Button>

        <Button
          variant='ghost'
          onClick={() => deleteLecture(chapterId, lecture.id)}
          className='p-2 hover:bg-neutral-200 group'
        >
          <Trash2 className='size-5 group-hover:text-red-600' />
        </Button>
      </div>

      <DialogGroup
        dialogOpen={dialogOpen}
        setDialogOpen={setDialogOpen}
        lecture={lecture}
        chapterId={chapterId}
      />
    </CustomDraggable>
  );
}

const LecturesCard = ({ chapterId, lectures }: LecturesProps) => {
  return (
    <div className='mt-3 space-y-3'>
      {lectures.map((lecture, index) => (
        <LectureItem
          key={lecture.id}
          lecture={lecture}
          index={index}
          chapterId={chapterId}
          lectureLength={lectures.length}
        />
      ))}
    </div>
  );
};

export default LecturesCard;
