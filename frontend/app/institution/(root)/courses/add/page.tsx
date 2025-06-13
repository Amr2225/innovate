import React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import BasInfo from "./_components/basic-info";
import Curriculum from "../_components/curriculum";
import PublishCoursePage from "../_components/publish-course";
import Link from "next/link";

// type CreateCourseTabs = "info" | "advanced-info" | "curriculum" | "publish";

export default function AddCoursePage() {
  // const [activeTab, setActiveTab] = useState<CreateCourseTabs>("info");

  return (
    <Tabs defaultValue={"info"}>
      <TabsList className='grid w-full grid-cols-3' defaultValue={"info"}>
        <TabsTrigger value='info'>Course Information</TabsTrigger>
        <TabsTrigger value='curriculum'>Curriculum</TabsTrigger>
        <TabsTrigger value='publish'>Publish Course</TabsTrigger>
      </TabsList>
      <TabsContent value='info'>
        <div className='p-5 overflow-y-auto'>
          <div className='flex justify-between items-center'>
            <h1 className='text-3xl font-bold'>Course Information</h1>
            <Button variant='link' asChild>
              <Link href={`/institution/courses/preview`}>Preview</Link>
            </Button>
          </div>

          <BasInfo />
        </div>
      </TabsContent>

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
