"use client";
import React, { useState, useEffect, useMemo } from "react";
import { useParams } from "next/navigation";
import { getCourseById } from "@/apiService/courseService";
import { useQuery } from "@tanstack/react-query";
import LectureDetails from "@/components/lectureDetails";
import CourseContent from "@/components/courseContent";
import { Chapter, Lecture, LectureResponse } from "@/types/course.type";
import { Loader2 } from "lucide-react";

export default function WatchCoursePage() {
  const { courseId } = useParams();
  const { data, isLoading } = useQuery({
    queryKey: ["course", courseId],
    queryFn: () => getCourseById(courseId as string),
  });

  const [activeLecture, setActiveLecture] = useState<(LectureResponse & Lecture) | null>(null);

  const lectureNumber = useMemo(() => {
    if (!activeLecture || isLoading) return null;

    const chapter = data?.chapters.find((chapter) =>
      chapter.lectures.some((lecture) => lecture.id === activeLecture.id)
    );

    const lectureIndex = chapter?.lectures.findIndex((lecture) => lecture.id === activeLecture.id);
    return lectureIndex! + 1;
  }, [activeLecture, data?.chapters, isLoading]);

  useEffect(() => {
    if (!isLoading) {
      setActiveLecture(data?.chapters[0].lectures[0] as Lecture & LectureResponse);
    }
  }, [data?.chapters, isLoading]);

  if (isLoading) {
    return (
      <div className='flex h-[50vh] items-center justify-center'>
        <Loader2 className='w-10 h-10 animate-spin text-primary' />
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
          incommingChapters={data?.chapters as Chapter[]}
        />
      </section>
    </div>
  );
}
