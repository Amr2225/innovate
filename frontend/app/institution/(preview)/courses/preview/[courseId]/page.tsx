"use client";
import React, { useMemo, useState } from "react";
import { useParams } from "next/navigation";

// Store
import { createCourseStore } from "@/store/courseStore";

// Components
import CourseContent from "@/components/courseContent";
import LectureDetails from "@/components/lectureDetails";

// Types
import { Lecture, LectureResponse } from "@/types/course.type";

// Icons
import { Loader2 } from "lucide-react";

export default function CoursePreviewPage() {
  const { courseId } = useParams();
  const useCourseStore = createCourseStore(courseId as string);
  const { chapters } = useCourseStore();

  const [activeLecture, setActiveLecture] = useState<(Lecture & LectureResponse) | null>(
    chapters[0].lectures[0] as Lecture & LectureResponse
  );

  const lectureNumber = useMemo(() => {
    if (!activeLecture) return null;

    const chapter = chapters.find((chapter) =>
      chapter.lectures.some((lecture) => lecture.id === activeLecture.id)
    );

    const lectureIndex = chapter?.lectures.findIndex((lecture) => lecture.id === activeLecture.id);
    return lectureIndex! + 1;
  }, [activeLecture, chapters]);

  if (chapters.length === 0) {
    return (
      <div className='flex h-[50vh] items-center justify-center'>
        <p className='text-lg text-neutral-500 font-medium'>No chapters found</p>
      </div>
    );
  }

  if (!activeLecture) {
    return (
      <div className='flex h-[50vh] items-center justify-center'>
        <Loader2 className='w-10 h-10 animate-spin' />
      </div>
    );
  }

  return (
    <div className='grid grid-cols-3 gap-4 pb-5'>
      <section className='col-span-2'>
        <LectureDetails
          lecture={activeLecture as Lecture & LectureResponse}
          lectureNumber={lectureNumber}
        />
      </section>
      <section>
        <CourseContent
          activeLecture={activeLecture as Lecture & LectureResponse}
          setActiveLecture={setActiveLecture}
        />
      </section>
    </div>
  );
}
