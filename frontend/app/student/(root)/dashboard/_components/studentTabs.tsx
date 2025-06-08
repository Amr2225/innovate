import React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

// Tabs Sections
import DashboardSection from "./TabsPages/dashboard";
import CousresSection from "./TabsPages/courses";
import EnrollSection from "./TabsPages/Enroll";
import SettingsSection from "./TabsPages/settings";
import AssignmentSection from "./TabsPages/assignmentSection";

export default function StudentTabs({ name }: { name: string }) {
  return (
    <Tabs defaultValue='dashboard'>
      <TabsList className='w-full grid grid-cols-8 py-2'>
        <TabsTrigger value='dashboard'>Dashboard</TabsTrigger>
        <TabsTrigger value='courses'>Courses</TabsTrigger>
        <TabsTrigger value='assignments'>Assignments</TabsTrigger>
        <TabsTrigger value='exams'>Exams</TabsTrigger>
        <TabsTrigger value='teachers'>Teachers</TabsTrigger>
        <TabsTrigger value='messages'>Messages</TabsTrigger>
        <TabsTrigger value='enroll'>Enroll</TabsTrigger>
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

      <TabsContent value='enroll'>
        <EnrollSection />
      </TabsContent>

      <TabsContent value='settings'>
        <SettingsSection />
      </TabsContent>
    </Tabs>
  );
}
