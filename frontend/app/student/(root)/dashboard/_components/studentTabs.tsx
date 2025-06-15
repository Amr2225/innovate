import React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

// Tabs Sections
import DashboardSection from "./TabsPages/dashboard";
import CousresSection from "./TabsPages/courses";
import EnrollSection from "./TabsPages/Enroll";
import SettingsSection from "./TabsPages/settings";
import AssignmentSection from "./TabsPages/assignmentSection";
import QuizSection from "./TabsPages/quizSection";
import ExamSection from "./TabsPages/examSection";
import CourseGradesSection from "./TabsPages/courseGradesSection";

export default function StudentTabs({ name }: { name: string }) {
  return (
    <Tabs defaultValue='dashboard'>
      <TabsList className='w-full grid grid-cols-8 py-2'>
        <TabsTrigger value='dashboard'>Dashboard</TabsTrigger>
        <TabsTrigger value='courses'>Courses</TabsTrigger>
        <TabsTrigger value='assignments'>Assignments</TabsTrigger>
        <TabsTrigger value='quizzes'>Quizzes</TabsTrigger>
        <TabsTrigger value='exams'>Exams</TabsTrigger>
        <TabsTrigger value='enroll'>Enroll</TabsTrigger>
        <TabsTrigger value='courseGrades'>Course Grades</TabsTrigger>
        <TabsTrigger value='settings'>Settings</TabsTrigger>
      </TabsList>

      <TabsContent value='dashboard'>
        <DashboardSection name={name} />
      </TabsContent>

      <TabsContent value='courses'>
        <CousresSection />
      </TabsContent>

      <TabsContent value='assignments'>
        <AssignmentSection />
      </TabsContent>

      <TabsContent value='quizzes'>
        <QuizSection />
      </TabsContent>

      <TabsContent value='exams'>
        <ExamSection />
      </TabsContent>

      <TabsContent value='enroll'>
        <EnrollSection />
      </TabsContent>

      <TabsContent value='courseGrades'>
        <CourseGradesSection />
      </TabsContent>

      <TabsContent value='settings'>
        <SettingsSection />
      </TabsContent>
    </Tabs>
  );
}
