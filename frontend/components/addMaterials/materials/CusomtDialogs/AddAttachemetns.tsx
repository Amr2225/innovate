"use client";
import React, { useCallback } from "react";
import { AnimatePresence, motion } from "framer-motion";

// Components
import { Button } from "@/components/ui/button";
import { DialogClose } from "@/components/ui/dialog";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import CustomDialog from "@/components/CustomDialog";

// Icons
import { BookText, Paperclip } from "lucide-react";

// Utils
import { cn } from "@/lib/utils";
import { GetFileSizeFromBytes } from "@/lib/getFileSize";

// External libraries
import { useDropzone } from "react-dropzone";

// Types
import { DialogGroupProps } from "../dialogGroup";

// Store
import { createCourseStore } from "@/store/courseStore";

// Hooks
import { useParams } from "next/navigation";

export default function AddAttachmentDialog({
  dialogOpen,
  setDialogOpen,
  lecture,
  chapterId,
}: DialogGroupProps) {
  const { courseId } = useParams();
  const useCourseStore = createCourseStore((courseId as string) || "new");
  const { updateLecture } = useCourseStore();

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 1) {
        return;
      }
      updateLecture(chapterId, lecture.id, "attachments", acceptedFiles[0]);
    },
    [chapterId, lecture.id, updateLecture]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  if (!lecture) return null;

  return (
    <CustomDialog
      title='Attachment'
      description='Upload a attachment for the lecture'
      open={dialogOpen === "attachment"}
      setOpen={(open) => setDialogOpen(open ? "attachment" : null)}
    >
      <div
        className={cn(
          "flex justify-center items-center h-[150px] w-full rounded-md border border-neutral-300 overflow-hidden",
          `${lecture.attachments ? "border-none" : "border-neutral-300"}`
        )}
      >
        {!lecture.attachments ? (
          <div
            {...getRootProps()}
            className='flex justify-center items-center w-full h-full flex-col gap-2 cursor-pointer'
          >
            <input {...getInputProps()} accept='.pdf,.doc,.docx,.xls,.xlsx,.csv,.txt' />
            <Paperclip
              className={cn("size-10 text-neutral-400", {
                "text-primary": isDragActive,
              })}
            />
            <p
              className={cn("text-neutral-400 flex flex-col gap-1 items-center", {
                "text-primary": isDragActive,
              })}
            >
              <span
                className={cn("font-medium text-neutral-500", {
                  "text-primary": isDragActive,
                })}
              >
                Attach File
              </span>
              <span>Drag an drop a file or browse file</span>
            </p>
          </div>
        ) : (
          <div className='w-full'>
            <AnimatePresence>
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
              >
                <Card>
                  <CardHeader>
                    <div className='flex items-center gap-3'>
                      <div className='bg-primary/15 rounded-full p-3'>
                        <BookText className='size-5 text-primary' />
                      </div>
                      <div className='space-y-0.5'>
                        <CardTitle className='text-sm'>{lecture.attachments?.name}</CardTitle>
                        <CardDescription className='uppercase text-xs'>
                          {GetFileSizeFromBytes(lecture.attachments?.size)}{" "}
                          {lecture.attachments?.file_extension}
                        </CardDescription>
                        {/* <CardDescription className='uppercase text-xs'>
                          {lecture.attachments?.file_extension}
                        </CardDescription> */}
                      </div>
                    </div>
                  </CardHeader>
                </Card>
              </motion.div>
            </AnimatePresence>
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
          {lecture.attachments && (
            <Button
              variant='link'
              onClick={() => updateLecture(chapterId, lecture.id, "attachments", null)}
            >
              Reset
            </Button>
          )}
        </div>
        <Button>Upload</Button>
      </div>
    </CustomDialog>
  );
}
