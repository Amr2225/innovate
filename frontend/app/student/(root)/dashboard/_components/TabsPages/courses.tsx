"use client";
import React from "react";
import {
  Select,
  SelectValue,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from "@/components/ui/select";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";

import CourseCard from "../courseCard";
import { getStudentCourses } from "@/apiService/enrollmentService";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { studentAnalytics } from "@/apiService/analytics";

export default function CousresSection() {
  const { data: coursesData, isLoading: coursesLoading } = useQuery({
    queryKey: ["student-courses"],
    queryFn: () => getStudentCourses({ page_size: 1000, pageParam: 1 }),
  });

  const { data: dashboardData, isLoading: dashboardLoading } = useQuery({
    queryKey: ["student-dashboard"],
    queryFn: () => studentAnalytics(),
  });

  return (
    <div>
      {dashboardLoading ? (
        <Skeleton className='w-full h-[50px]' />
      ) : (
        <h1 className='text-xl font-bold mt-3'>Courses ({dashboardData?.course_count})</h1>
      )}
      <div className='grid grid-cols-5 items-center gap-4 mb-5'>
        <div className='col-span-2'>
          <Label htmlFor='search'>Search:</Label>
          <Input id='search' placeholder='Search in your courses..' />
        </div>

        <div>
          <Label>Sort by:</Label>
          <Select defaultValue='latest'>
            <SelectTrigger className='w-full'>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='latest'>Latest</SelectItem>
              <SelectItem value='earliest'>Earliest</SelectItem>
              <SelectItem value='alphabetical'>Alphabetical</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor='sort'>Status:</Label>
          <Select defaultValue='latest'>
            <SelectTrigger className='w-full'>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='latest'>Latest</SelectItem>
              <SelectItem value='earliest'>Earliest</SelectItem>
              <SelectItem value='alphabetical'>Alphabetical</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor='sort'>Teacher:</Label>
          <Select defaultValue='latest'>
            <SelectTrigger className='w-full'>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='latest'>Latest</SelectItem>
              <SelectItem value='earliest'>Earliest</SelectItem>
              <SelectItem value='alphabetical'>Alphabetical</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className='grid grid-cols-4 gap-4 pb-5'>
        {coursesLoading ? (
          <Skeleton className='w-full h-[50px]' />
        ) : coursesData?.length && coursesData?.length > 0 ? (
          coursesData?.map((course) => (
            <CourseCard
              key={course.id}
              courseName={course.name}
              courseDescription={course.description}
              courseId={course.id}
            />
          ))
        ) : (
          <p className='text-2xl font-semibold text-center text-gray-500 col-span-4'>
            No lectures found
          </p>
        )}
      </div>
    </div>
  );
}
