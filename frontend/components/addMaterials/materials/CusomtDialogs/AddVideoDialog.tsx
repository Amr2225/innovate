"use client";
import React, { useCallback } from "react";

// External libraries
import Player from "next-video/player";

// Components
import { Button } from "@/components/ui/button";
import { DialogClose } from "@/components/ui/dialog";
import CustomDialog from "@/components/CustomDialog";

// Icons
import { Video } from "lucide-react";

// Utils
import { cn } from "@/lib/utils";
import useVideo from "@/hooks/useVideo";

// External libraries
import { useDropzone } from "react-dropzone";

// Types
import { DialogGroupProps } from "../dialogGroup";

// Store
import { createCourseStore } from "@/store/courseStore";

// Hooks
import { useParams } from "next/navigation";

export default function AddVideoDialog({
  dialogOpen,
  setDialogOpen,
  lecture,
  chapterId,
}: DialogGroupProps) {
  // Load video from IndexedDB
  const { previewUrl } = useVideo(lecture.video?.storageKey as string);
  const { courseId } = useParams();
  const useCourseStore = createCourseStore((courseId as string) || "new");
  const { updateLecture } = useCourseStore();

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 1) {
        return;
      }
      updateLecture(chapterId, lecture.id, "video", acceptedFiles[0]);
    },
    [chapterId, lecture.id, updateLecture]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
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
      <div className='flex justify-between items-center gap-2 mt-2'>
        <div className='space-x-2'>
          <DialogClose asChild>
            <Button type='button' variant='secondary'>
              Close
            </Button>
          </DialogClose>
        </div>
        {lecture.video && (
          <Button
            // variant='link'
            onClick={() => updateLecture(chapterId, lecture.id, "video", null)}
          >
            Reset
          </Button>
        )}
        {/* <Button>Upload</Button> */}
      </div>
    </CustomDialog>
  );
}
