import React from "react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { CirclePlay, Paperclip, Clock, Loader2 } from "lucide-react";

// Store
// import { useCourseStore } from "@/store/courseStore";
import { Button } from "@/components/ui/button";
import { useUploadCourse } from "@/queryHooks/useUploadCourse";
import { createCourseStore } from "@/store/courseStore";

export default function PublishCoursePage() {
  const useCourseStore = createCourseStore(undefined);
  const { course, chapters } = useCourseStore();
  const { UploadCourse, isCreating } = useUploadCourse("");

  return (
    <div className='mt-5'>
      <div>
        <h1 className='text-xl font-semibold mb-1.5'>{course?.name}</h1>
      </div>

      <Accordion type='multiple' className='space-y-3'>
        {chapters.map((chapter, index) => (
          <AccordionItem
            key={chapter.id}
            value={`item-${chapter.id}`}
            className='border pt-1 rounded-md '
          >
            <AccordionTrigger className='hover:no-underline px-3'>
              <span className='space-y-1'>
                <h4 className='text-base'>
                  Chapter {index + 1}: {chapter.title}
                </h4>
                <p className='text-sm text-muted-foreground'>{chapter.lectures.length} Lectures</p>
              </span>
            </AccordionTrigger>
            {chapter.lectures.map((lecture) => (
              <AccordionContent className='border-t pt-2 hover:bg-neutral-100' key={lecture.id}>
                <div className='flex items-start gap-2 px-3'>
                  <CirclePlay className='size-4 text-primary' />
                  <div className='space-y-1'>
                    <h5 className='text-sm'>{lecture.title}</h5>
                    <div className='flex items-center justify-start gap-2 text-xs text-muted-foreground'>
                      {lecture.video && (
                        <p className='flex items-center gap-1 text-muted-foreground'>
                          <Clock className='size-3' /> {lecture.duration}
                        </p>
                      )}
                      {lecture.attachments && (
                        <p className='flex items-center gap-1 text-muted-foreground'>
                          <Paperclip className='size-3' /> 2
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </AccordionContent>
            ))}
          </AccordionItem>
        ))}
      </Accordion>

      <div className='mt-5 flex justify-end items-center'>
        <Button type='button' onClick={UploadCourse} disabled={isCreating}>
          {isCreating ? <Loader2 className='size-3 animate-spin' /> : "Upload Course"}
        </Button>
      </div>
    </div>
  );
}
