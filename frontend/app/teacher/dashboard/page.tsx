import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import React from "react";

import StudentsPerCourse from "./_analytics/studentsPerCourse";
import CourseAvgScore from "./_analytics/courseAvgScore";
import TotalCourses from "./_analytics/totalCourses";
import TotalStudentsCourse from "./_analytics/totalStudentsCourse";
import { BookOpen, Users } from "lucide-react";
import AvgCompletionRate from "./_analytics/avgCompletionRate";
import TopStudents from "./_analytics/topStudents";

export default function TeacherDashboard() {
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
          <CardDescription>Total number of active courses you are teaching</CardDescription>
          <CardContent>
            <TotalCourses />
          </CardContent>
        </CardHeader>
      </Card>

      <Card className='col-span-2 '>
        <CardHeader>
          <CardTitle>
            <div className='flex items-center gap-2'>
              <Users className='size-4' />
              Total Students
            </div>
          </CardTitle>
          <CardDescription>Total number of active students you are teaching</CardDescription>
          <CardContent>
            <TotalStudentsCourse />
          </CardContent>
        </CardHeader>
      </Card>

      <Card className='col-span-2'>
        <CardHeader>
          <CardTitle>Avg Completion Rate</CardTitle>
          <CardDescription>Average completion rate of your courses</CardDescription>
          <CardContent>
            <AvgCompletionRate />
          </CardContent>
        </CardHeader>
      </Card>

      <Card className='col-span-3'>
        <CardHeader>
          <CardTitle>Course Avg Score</CardTitle>
          <CardDescription>Average score distribution across different courses</CardDescription>
          <CardContent>
            <CourseAvgScore />
          </CardContent>
        </CardHeader>
      </Card>

      <Card className='col-span-3'>
        <CardHeader>
          <CardTitle>Students Per Course</CardTitle>
          <CardDescription>Number of active students enrolled in each course</CardDescription>
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
