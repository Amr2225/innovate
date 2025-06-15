"use client";

import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Info } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useQuery } from "@tanstack/react-query";
import { getCourseGrades } from "@/apiService/enrollmentService";

function InfoDisplay({ message }: { message: string }) {
  return (
    <Card className='border-blue-200 bg-blue-50/50 mt-12'>
      <CardHeader>
        <div className='flex items-center gap-2 text-blue-600'>
          <Info className='h-5 w-5' />
          <CardTitle>Course Grades</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className='space-y-4'>
          <p className='text-muted-foreground'>{message}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function CourseGradesSection() {
  const {
    data: grades,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["course-grades"],
    queryFn: getCourseGrades,
  });

  if (isLoading) {
    return (
      <div className='flex items-center justify-center h-64'>
        <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-primary'></div>
      </div>
    );
  }

  if (error || !grades) {
    return (
      <InfoDisplay
        message={
          error instanceof Error
            ? error.message
            : "No grades available at this time. Please check back later."
        }
      />
    );
  }

  return (
    <div>
      <h1 className='text-xl font-bold mt-3 mb-6'>Course Grades</h1>
      <div className='border rounded-lg overflow-hidden bg-card'>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Course Name</TableHead>
              <TableHead>Level</TableHead>
              <TableHead>Semester</TableHead>
              <TableHead>Grade</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {grades.map((course) => (
              <TableRow key={course.course_id}>
                <TableCell className='font-medium'>{course.course_name}</TableCell>
                <TableCell>Level {Math.ceil(course.semester / 2)}</TableCell>
                <TableCell>Semester {course.semester % 2 || 2}</TableCell>
                <TableCell>
                  {course.grade}/{course.total_grade}
                </TableCell>
                <TableCell>
                  <Badge
                    variant={course.is_passed ? "default" : "destructive"}
                    className='capitalize'
                  >
                    {course.is_passed ? "Passed" : "Failed"}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
