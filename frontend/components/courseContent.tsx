import React, { useMemo } from "react";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Checkbox } from "@/components/ui/checkbox";

import { Video, Play } from "lucide-react";
import { cn } from "@/lib/utils";
import { Progress } from "./ui/progress";
import { Chapter, Lecture, LectureResponse } from "@/types/course.type";
import { createCourseStore } from "@/store/courseStore";

interface CourseContentProps {
  activeLecture: (Lecture & LectureResponse) | null;
  setActiveLecture: React.Dispatch<React.SetStateAction<(Lecture & LectureResponse) | null>>;
  incommingChapters?: Chapter[];
}

export default function CourseContent({
  activeLecture,
  setActiveLecture,
  incommingChapters,
}: CourseContentProps) {
  const useCourseStore = createCourseStore("new");
  const { chapters } = useCourseStore();

  const currentChapter = useMemo(() => {
    if (incommingChapters && incommingChapters.length > 0) return incommingChapters;
    else return chapters;
  }, [chapters, incommingChapters]);

  // if (!activeLecture) return null;

  return (
    <div className='space-y-3'>
      <div className='space-y-1'>
        <span className='flex items-center justify-between gap-2'>
          <h1 className='text-xl font-bold'>Course Content</h1>
          <p className='text-xs text-green-500 font-semibold'>15% Completed</p>
        </span>
        <Progress
          value={15}
          className='w-full h-1.5'
          //   style={{ "--primary": "142 70.6 45.3%" } as React.CSSProperties}
        />
      </div>
      <Accordion type='multiple' className='space-y-3'>
        {currentChapter.map((chapter) => (
          <AccordionItem
            key={chapter.id}
            value={`item-${chapter.id}`}
            className='border rounded-md'
          >
            <AccordionTrigger
              arrowPosition='left'
              className='hover:no-underline px-3 data-[state=open]:text-primary data-[state=open]:bg-neutral-100'
            >
              <ChapterAttributes
                chapterName={chapter.title}
                lecturesAmount={chapter.lectures.length}
                totalDuration={"51m"}
                completedPercentage={"25%"}
              />
            </AccordionTrigger>
            {chapter.lectures.map((lecture, index) => (
              <AccordionContent
                key={lecture.id}
                onClick={() => setActiveLecture(lecture as Lecture & LectureResponse)}
                className={cn(
                  "border-t py-3.5  hover:bg-primary/10 hover:text-black text-muted-foreground cursor-pointer",
                  activeLecture?.id === lecture.id && "bg-primary/10 text-black"
                )}
              >
                <div className='flex items-start justify-between gap-2 px-3'>
                  <span className='flex items-center gap-2'>
                    <Checkbox
                      className='size-3 text-primary grid place-content-center'
                      checkClassName='size-3'
                      checked={false}
                      onCheckedChange={() => null}
                    />
                    <h5 className='text-[13px]'>
                      {index + 1}.{lecture.title}
                    </h5>
                  </span>
                  <span className='flex items-center justify-center gap-2 text-xs'>
                    <Play className='size-3' />
                    <p>{lecture.duration}</p>
                    {/* TODO: if active change icon */}
                    {/* <Pause className='size-3' /> */}
                  </span>
                </div>
              </AccordionContent>
            ))}
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
}

function ChapterAttributes({
  chapterName,
  lecturesAmount,
}: // totalDuration,
// completedPercentage,
{
  chapterName: string;
  lecturesAmount: number;
  totalDuration: string;
  completedPercentage: string;
}) {
  return (
    <div>
      <h4>{chapterName}</h4>
      <span className='text-xs text-muted-foreground flex items-center gap-2'>
        <span className='flex items-center gap-1'>
          <Video className='size-3 text-purple-800' />
          <p className='text-neutral-500'>{lecturesAmount} Lectures</p>
        </span>
        {/* <span className='flex items-center gap-1'>
          <Clock className='size-3 text-primary' />
          <p className='text-neutral-500'>{totalDuration}</p>
        </span>
        <span className='flex items-center gap-1'>
          <CheckCheck className='size-3 text-green-500' />
          <p className='text-neutral-500'>{completedPercentage} Completed (1/4)</p>
        </span> */}
      </span>
    </div>
  );
}
