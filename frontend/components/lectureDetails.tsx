import { Lecture } from "@/types/course.type";
import moment from "moment";
import Player from "next-video/player";
import React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import useVideo from "@/hooks/useVideo";

export default function LectureDetails({
  lecture,
  lectureNumber,
}: {
  lecture: Lecture;
  lectureNumber: number | null;
}) {
  const { previewUrl } = useVideo(lecture.video?.storageKey as string);

  return (
    <div className='w-full'>
      <Player src={previewUrl as string} />

      <div>
        <h1 className='text-2xl mt-4'>
          {lectureNumber}.{lecture.title}
        </h1>
        <span className='text-sm text-muted-foreground mt-1'>
          <span className='flex items-center gap-2 text-xs'>
            <p className='text-muted-foreground'>Last updated:</p>
            <p className='text-black'>{moment().format("MMM DD, YYYY")}</p>
          </span>
        </span>
      </div>

      <Tabs defaultValue='description'>
        <TabsList className='w-full grid grid-cols-2'>
          <TabsTrigger value='description'>Description</TabsTrigger>
          <TabsTrigger value='attachments'>Attachments</TabsTrigger>
        </TabsList>

        <TabsContent value='description'>
          <h1 className='text-lg font-bold'>Description</h1>
          <p>{lecture.description}</p>
        </TabsContent>

        <TabsContent value='attachments'>
          <h1 className='text-lg font-bold'>Attachments</h1>
          <p>{lecture.attachments?.name}</p>
        </TabsContent>
      </Tabs>
    </div>
  );
}
