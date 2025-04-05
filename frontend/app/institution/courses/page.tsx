"use client";
import React, { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import BasInfo from "./_components/basic-info";

type CreateCourseTabs = "basic-info" | "advanced-info" | "curriculum" | "publish";

export default function InstitutionCourses() {
  const [activeTab, setActiveTab] = useState<CreateCourseTabs>("basic-info");
  return (
    <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as CreateCourseTabs)}>
      <TabsList className='grid w-full grid-cols-4' defaultValue={"basic-info"}>
        <TabsTrigger value='basic-info'>Basic Informaiton</TabsTrigger>
        <TabsTrigger value='advanced-info'>Advanced Information</TabsTrigger>
        <TabsTrigger value='Curriculum'>Curriculum</TabsTrigger>
        <TabsTrigger value='publish'>Publish Course</TabsTrigger>
      </TabsList>
      <TabsContent value='basic-info'>
        <div className='p-5'>
          <div className='flex justify-between items-center'>
            <h1 className='text-3xl font-bold'>Basic Information</h1>
            <div>
              <Button variant='secondary'>Save</Button>
              <Button variant='link'>Save & Preview</Button>
            </div>
          </div>

          <BasInfo />
          <div className='flex justify-between items-center mt-10'>
            <Button
              type='button'
              variant={"secondary"}
              onClick={() => setActiveTab("advanced-info")}
            >
              Next
            </Button>
          </div>
        </div>
      </TabsContent>

      <TabsContent value='advanced-info'>
        <div>
          <div>
            <h1>Advanced Information</h1>
          </div>
        </div>
      </TabsContent>
    </Tabs>
  );
}
