import React, { useCallback, useState } from "react";

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
import { CreateLecture, CreateChapter } from "@/types/course.type";
import { cn } from "@/lib/utils";

type CustomLecture = {
  id: string;
  title: string;
  description: string;
  video: string;
  attachments: string[];
};

type CustomChapter = {
  id: string;
  title: string;
  description: string;
  lectures: CustomLecture[];
};

interface LecturesProps {
  chapterId: string;
  lectures: CustomLecture[];
  deleteLecture: (chapterId: string, lectureId: string) => void;
  updateLecture: (chapterId: string, lectureId: string, title: string) => void;
}

export default function Curriculum() {
  const [chapters, setChapters] = useState<CustomChapter[]>([]);
  const [chapterId, setChapterId] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(Array(chapters.length).fill(false));

  const addLecture = (chapterId: string) => {
    setChapters((prev) =>
      prev.map((chapter) =>
        chapter.id === chapterId
          ? {
              ...chapter,
              lectures: [
                ...chapter.lectures,
                {
                  id: Math.random().toString(),
                  title: "New Lecture",
                  description: "New Lecture Description",
                  video: "",
                  attachments: [],
                },
              ],
            }
          : chapter
      )
    );
  };

  const deleteLecture = (chapterId: string, lectureId: string) => {
    setChapters((prev) =>
      prev.map((chapter) =>
        chapter.id === chapterId
          ? { ...chapter, lectures: chapter.lectures.filter((l) => l.id !== lectureId) }
          : chapter
      )
    );
  };

  const updateLecture = (chapterId: string, lectureId: string, title: string) => {
    setChapters((prev) =>
      prev.map((chapter) =>
        chapter.id === chapterId
          ? {
              ...chapter,
              lectures: chapter.lectures.map((storedLecture) =>
                storedLecture.id === lectureId ? { ...storedLecture, title } : storedLecture
              ),
            }
          : chapter
      )
    );
  };

  const updateChapter = (chapterId: string, key: string, value: string) => {
    setChapters((prev) =>
      prev.map((chapter) => (chapter.id === chapterId ? { ...chapter, [key]: value } : chapter))
    );
  };

  const addChapter = () => {
    setChapters([
      ...chapters,
      {
        id: Math.random().toString(),
        title: "New Chapter",
        description: "New Chapter Description",
        lectures: [],
      },
    ]);
  };

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
        attachments: null,
        chapter: chapterId,
      });
  };

  return (
    <section className='h-full w-full'>
      {chapters.map((chapter, index) => (
        <div key={index} className='bg-neutral-100 rounded-lg p-5 my-5'>
          <header className='flex justify-between items-center'>
            <div className='flex justify-start gap-3 items-center'>
              <Menu className='size-5' />
              <EditInput
                isEditing={isEditing[index]}
                closeEditing={() => {
                  const newIsEditing = [...isEditing];
                  newIsEditing[index] = false;
                  return setIsEditing(newIsEditing);
                }}
                value={chapter.title}
                setValue={(value) => {
                  updateChapter(chapter.id, "title", value);
                }}
                textStyle='text-base'
              />
              <EditInput
                isEditing={isEditing[index]}
                closeEditing={() => {
                  const newIsEditing = [...isEditing];
                  newIsEditing[index] = false;
                  return setIsEditing(newIsEditing);
                }}
                value={chapter.description}
                setValue={(value) => {
                  updateChapter(chapter.id, "description", value);
                }}
                textStyle='font-normal text-base'
              />
            </div>

            <div className='flex items-center gap-2'>
              <Button
                variant='ghost'
                onClick={() => addLecture(chapter.id)}
                className='p-2 hover:bg-neutral-200'
              >
                <Plus className='size-5' />
              </Button>
              <Button
                variant='ghost'
                onClick={() =>
                  setIsEditing((prev) => {
                    const newIsEditing = [...prev];
                    newIsEditing[index] = !newIsEditing[index];
                    return newIsEditing;
                  })
                }
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
            deleteLecture={deleteLecture}
            updateLecture={updateLecture}
          />
        </div>
      ))}
      <Button variant='secondary' className='w-full py-5 font-semibold mt-2' onClick={addChapter}>
        <Plus className='size-5 mr-1' />
        Add Chapter
      </Button>

      <Button type='button' onClick={handleCreation}>
        Submit
      </Button>
    </section>
  );
}

const LecturesCard = ({ chapterId, lectures, deleteLecture, updateLecture }: LecturesProps) => {
  const [isEditing, setIsEditing] = useState(Array(lectures.length).fill(false));
  const [dialogOpen, setDialogOpen] = useState<string | null>(null);
  const [video, setVideo] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 1) {
      return;
    }
    console.log(acceptedFiles);
    setVideo(acceptedFiles[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <div className='mt-3 space-y-3'>
      {lectures.map((lecture, index) => (
        <div
          key={lecture.id}
          className='flex justify-between gap-3 items-center bg-white p-5 text-neutral-600'
        >
          <div className='flex justify-start gap-3 items-center'>
            <Menu className='size-5' />
            <EditInput
              isEditing={isEditing[index]}
              closeEditing={() => {
                const newIsEditing = [...isEditing];
                newIsEditing[index] = false;
                return setIsEditing(newIsEditing);
              }}
              value={lecture.title}
              setValue={(value) => {
                updateLecture(chapterId, lecture.id, value);
              }}
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
                <DropdownMenuItem onClick={() => setDialogOpen("video")}>Video</DropdownMenuItem>
                <DropdownMenuItem>Attach File</DropdownMenuItem>
                <DropdownMenuItem>Captions</DropdownMenuItem>
                <DropdownMenuItem>Description</DropdownMenuItem>
                <DropdownMenuItem>Lecture Notes</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Button
              variant='ghost'
              onClick={() =>
                setIsEditing((prev) => {
                  const newIsEditing = [...prev];
                  newIsEditing[index] = !newIsEditing[index];
                  return newIsEditing;
                })
              }
              className='p-2 hover:bg-neutral-200'
            >
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
        </div>
      ))}

      <CustomDialog
        title='Video'
        description='Upload a video for the lecture'
        open={dialogOpen === "video"}
        setOpen={(open) => setDialogOpen(open ? "video" : null)}
      >
        <div className='flex justify-center items-center h-[250px] w-full rounded-md border border-neutral-300 overflow-hidden'>
          {!video ? (
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
              <video src={URL.createObjectURL(video)} autoPlay muted loop controls />
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
            {video && (
              <Button variant='link' onClick={() => setVideo(null)}>
                Reset
              </Button>
            )}
          </div>
          <Button>Upload</Button>
        </div>
      </CustomDialog>
    </div>
  );
};
