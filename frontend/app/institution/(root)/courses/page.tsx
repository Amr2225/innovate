"use client";
import React, { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import BasInfo from "./_components/basic-info";
import Curriculum from "./_components/curriculum";
import PublishCoursePage from "./_components/publish-course";

type CreateCourseTabs = "info" | "advanced-info" | "curriculum" | "publish";

export default function InstitutionCourses() {
  const [activeTab, setActiveTab] = useState<CreateCourseTabs>("info");

  return (
    <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as CreateCourseTabs)}>
      <TabsList className='grid w-full grid-cols-3' defaultValue={"info"}>
        <TabsTrigger value='info'>Course Information</TabsTrigger>
        {/* <TabsTrigger value='advanced-info'>Advanced Information</TabsTrigger> */}
        <TabsTrigger value='curriculum'>Curriculum</TabsTrigger>
        <TabsTrigger value='publish'>Publish Course</TabsTrigger>
      </TabsList>
      <TabsContent value='info'>
        <div className='p-5 overflow-y-auto'>
          <div className='flex justify-between items-center'>
            <h1 className='text-3xl font-bold'>Course Information</h1>
            <div>
              <Button variant='secondary'>Save</Button>
              <Button variant='link'>Save & Preview</Button>
            </div>
          </div>

          <BasInfo />
          {/* <div className='flex justify-between items-center mt-10'>
            <Button type='button' variant={"secondary"} onClick={() => setActiveTab("curriculum")}>
              Next
            </Button>
          </div> */}
        </div>
      </TabsContent>

      <TabsContent value='curriculum'>
        <div className='p-5'>
          <div className='flex justify-between items-center'>
            <h1 className='text-3xl font-bold'>Course Curriculum</h1>
            <div>
              <Button variant='secondary'>Save</Button>
              <Button variant='link'>Save & Preview</Button>
            </div>
          </div>
          <Curriculum />
        </div>
      </TabsContent>

      <TabsContent value='publish'>
        <div className='p-5'>
          <div className='flex justify-between items-center'>
            <h1 className='text-3xl font-bold'>Publish Course</h1>
            <div>
              <Button variant='secondary'>Save</Button>
              <Button variant='link'>Save & Preview</Button>
            </div>
          </div>
          <PublishCoursePage />
        </div>
      </TabsContent>
    </Tabs>
  );
}

/* <div className='flex justify-between items-center mt-10'>
            <Button
              type='button'
              variant={"secondary"}
              onClick={() => setActiveTab("advanced-info")}
            >
              Next
            </Button>
          </div> */
