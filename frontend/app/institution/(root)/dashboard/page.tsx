import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import React from "react";
import { BookOpen, Users } from "lucide-react";

import CourseCount from "./_analytics/courseCount";
import StudentsCount from "./_analytics/studentsCount";
import TeacherCount from "./_analytics/teacherCount";

import CourseAvgScore from "@/app/teacher/dashboard/_analytics/courseAvgScore";
import StudentsPerCourse from "@/app/teacher/dashboard/_analytics/studentsPerCourse";
import TopStudents from "@/app/teacher/dashboard/_analytics/topStudents";

export default function InstitutionDashboard() {
  return (
    <div className='grid grid-cols-1 md:grid-cols-6 gap-4'>
      <Card className='col-span-2'>
        <CardHeader>
          <CardTitle>
            <div className='flex items-center gap-2'>
              <BookOpen className='size-4' />
              Total Courses
            </div>
          </CardTitle>
          <CardDescription>Number of active courses in the institution</CardDescription>
          <CardContent>
            <CourseCount />
          </CardContent>
        </CardHeader>
      </Card>

      <Card className='col-span-2'>
        <CardHeader>
          <CardTitle>
            <div className='flex items-center gap-2'>
              <Users className='size-4' />
              Total Students
            </div>
          </CardTitle>
          <CardDescription>Total number of students in the institution</CardDescription>
          <CardContent>
            <StudentsCount />
          </CardContent>
        </CardHeader>
      </Card>

      <Card className='col-span-2'>
        <CardHeader>
          <CardTitle>
            <div className='flex items-center gap-2'>
              <Users className='size-4' />
              Total Teachers
            </div>
          </CardTitle>
          <CardDescription>Total number of teachers in the institution</CardDescription>
          <CardContent>
            <TeacherCount />
          </CardContent>
        </CardHeader>
      </Card>

      <Card className='col-span-3'>
        <CardHeader>
          <CardTitle>Course Avg Score</CardTitle>
          <CardDescription>
            Average score distribution across different courses in the institution
          </CardDescription>
          <CardContent>
            <CourseAvgScore />
          </CardContent>
        </CardHeader>
      </Card>

      <Card className='col-span-3'>
        <CardHeader>
          <CardTitle>Students Per Course</CardTitle>
          <CardDescription>
            Number of active students enrolled in each course in the institution
          </CardDescription>
          <CardContent>
            <StudentsPerCourse />
          </CardContent>
        </CardHeader>
      </Card>

      <Card className='col-span-6 h-full'>
        <CardHeader>
          <CardTitle>Top Students</CardTitle>
          <CardDescription>Showing Top 5 students in each course</CardDescription>
          <CardContent>
            <TopStudents />
          </CardContent>
        </CardHeader>
      </Card>
    </div>
  );
}
