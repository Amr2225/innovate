"use client";
import React from "react";
import Link from "next/link";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";

// Components
import Curriculum from "../_components/curriculum";
import PublishCoursePage from "../_components/publish-course";

// type CreateCourseTabs = "info" | "advanced-info" | "curriculum" | "publish";

export default function CoursePage() {
  return (
    <Tabs defaultValue={"curriculum"}>
      <TabsList className='grid w-full grid-cols-2' defaultValue={"curriculum"}>
        <TabsTrigger value='curriculum'>Curriculum</TabsTrigger>
        <TabsTrigger value='publish'>Publish Course</TabsTrigger>
      </TabsList>

      <TabsContent value='curriculum'>
        <div className='p-5'>
          <div className='flex justify-between items-center'>
            <h1 className='text-3xl font-bold'>Course Curriculum</h1>
            <Button variant='link' asChild>
              <Link href={`/institution/courses/preview`}>Preview</Link>
            </Button>
          </div>
          <Curriculum />
        </div>
      </TabsContent>

      <TabsContent value='publish'>
        <div className='p-5'>
          <div className='flex justify-between items-center'>
            <h1 className='text-3xl font-bold'>Publish Course</h1>
            <Button variant='link' asChild>
              <Link href={`/institution/courses/preview`}>Preview</Link>
            </Button>
          </div>
          <PublishCoursePage />
        </div>
      </TabsContent>
    </Tabs>
  );
}
