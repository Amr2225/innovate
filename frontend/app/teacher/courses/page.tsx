"use client";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableRow,
  TableHeader,
  TableHead,
  TableBody,
  TableCell,
} from "@/components/ui/table";
import React from "react";
import { Pencil, ChevronLeft, ChevronRight } from "lucide-react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { getCourses } from "@/apiService/courseService";
import { Course } from "@/types/course.type";
import { Skeleton } from "@/components/ui/skeleton";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import Link from "next/link";
import { useBreadcrumb } from "@/context/breadcrumbsContext";

interface TeacherCourseType {
  data: Course[];
  next: number | null;
  previous: number | null;
  page_size: number;
  total_pages: number;
  total_items: number;
}

export default function TeacherCourses() {
  const {
    data: courses,
    isLoading,
    hasNextPage,
    fetchNextPage,
    hasPreviousPage,
    fetchPreviousPage,
  } = useInfiniteQuery({
    queryKey: ["teacher-courses"],
    queryFn: ({ pageParam }) => getCourses<TeacherCourseType>({ page_size: 10, pageParam }),
    initialPageParam: 1,
    maxPages: 1,
    getNextPageParam: (lastPage) => lastPage.next,
    getPreviousPageParam: (firstPage) => firstPage.previous,
    select(data) {
      return data.pages.flatMap((page) => page.data);
    },
  });

  // TODO: make a skeleton loader
  if (isLoading)
    return (
      <div className='rounded-md border'>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>
                <Skeleton className='h-4 w-[100px]' />
              </TableHead>
              <TableHead>
                <Skeleton className='h-4 w-[100px]' />
              </TableHead>
              <TableHead>
                <Skeleton className='h-4 w-[100px]' />
              </TableHead>
              <TableHead>
                <Skeleton className='h-4 w-[100px]' />
              </TableHead>
              <TableHead>
                <Skeleton className='h-4 w-[100px]' />
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {[1, 2, 3].map((i) => (
              <TableRow key={i}>
                <TableCell>
                  <Skeleton className='h-8 w-[100px]' />
                </TableCell>
                <TableCell>
                  <Skeleton className='h-8 w-[100px]' />
                </TableCell>
                <TableCell>
                  <Skeleton className='h-8 w-[100px]' />
                </TableCell>
                <TableCell>
                  <Skeleton className='h-8 w-[100px]' />
                </TableCell>
                <TableCell>
                  <Skeleton className='h-8 w-[100px]' />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    );

  return (
    <div className='p-4'>
      <h1 className='text-2xl font-bold mb-2'>Courses</h1>
      <div className='rounded-md border'>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Course Name</TableHead>
              <TableHead>Description</TableHead>
              {/* If School Don't show this */}
              <TableHead>Total Grade</TableHead>
              <TableHead>Credit Hours</TableHead>
              <TableHead>Students</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {courses?.map((course) => (
              <TableRow key={course.id}>
                <TableCell>{course.name}</TableCell>
                <TableCell>{course.description}</TableCell>
                <TableCell>{course.total_grade}</TableCell>
                <TableCell>{course.credit_hours}</TableCell>
                <TableCell>32</TableCell>
                <TableCell>Active</TableCell>
                <TableCell>
                  <ActionsDropdown courseId={course.id} courseName={course.name} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className='flex justify-end mt-2'>
        <div className='flex gap-2'>
          <Button
            disabled={!hasPreviousPage}
            onClick={() => fetchPreviousPage()}
            variant='outline'
            size='icon'
          >
            <ChevronLeft className='h-4 w-4' />
          </Button>
          <Button
            disabled={!hasNextPage}
            onClick={() => fetchNextPage()}
            variant='outline'
            size='icon'
          >
            <ChevronRight className='h-4 w-4' />
          </Button>
        </div>
      </div>
    </div>
  );
}

function ActionsDropdown({ courseId, courseName }: { courseId: string; courseName: string }) {
  const { setMetadata } = useBreadcrumb();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant='outline' size='icon'>
          <Pencil className='h-4 w-4' />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align='end'>
        <DropdownMenuLabel>Actions</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          asChild
          onClick={() => setMetadata((prev) => prev.set(courseId, courseName))}
        >
          <Link href={`/teacher/courses/add-assignment/${courseId}`}>Add Assignment</Link>
        </DropdownMenuItem>
        <DropdownMenuItem>Add Quiz</DropdownMenuItem>
        <DropdownMenuItem>Add Exam</DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link href={`/teacher/courses/add-materials/${courseId}`}>Add Material</Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
