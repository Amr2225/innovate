"use client";

import React, { useEffect, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useQuery } from "@tanstack/react-query";
import { getTopStudents } from "@/apiService/analytics";
import { Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { getCourses } from "@/apiService/courseService";
import { Skeleton } from "@/components/ui/skeleton";

export default function TopStudents() {
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);

  const { data: courses, isLoading: isCoursesLoading } = useQuery({
    queryKey: ["courses"],
    queryFn: () => getCourses({ page_size: 1000 }),
  });

  const { data: topStudents, isLoading: isTopStudentsLoading } = useQuery({
    queryKey: ["top-students", selectedCourse],
    queryFn: () => getTopStudents({ courseId: selectedCourse || "" }),
    enabled: !!selectedCourse,
  });

  useEffect(() => {
    if (courses)
      if (courses?.data.length) {
        setSelectedCourse(courses.data[0].id);
      }
  }, [courses]);

  if (isTopStudentsLoading)
    return <Loader2 className='size-10 mx-auto animate-spin text-primary' />;

  return (
    <div className='space-y-4'>
      {/* Course Selector */}
      <div className='flex justify-end'>
        {isCoursesLoading ? (
          <Skeleton className='w-full h-[40px]' />
        ) : (
          <Select value={selectedCourse || ""} onValueChange={setSelectedCourse}>
            <SelectTrigger className='w-[200px]'>
              <SelectValue placeholder='Select a course' />
            </SelectTrigger>
            <SelectContent>
              {courses?.data.map((course) => (
                <SelectItem key={course.id} value={course.id}>
                  {course.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>

      {/* Students Table */}
      <div className='rounded-md border'>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Student</TableHead>
              <TableHead className='text-right'>Score</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {topStudents?.top_students.map((student) => (
              <TableRow key={student.student_id}>
                <TableCell>
                  <Badge variant='secondary'>{student.student_name}</Badge>
                </TableCell>
                <TableCell className='text-right'>
                  <span className='font-medium'>{student.total_grade}</span>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
