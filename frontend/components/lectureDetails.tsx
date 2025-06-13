import { Lecture, LectureResponse } from "@/types/course.type";
import moment from "moment";
import Player from "next-video/player";
import React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import useVideo from "@/hooks/useVideo";
import HtmlParser from "html-react-parser";
import styles from "@/components/addMaterials/materials/CusomtDialogs/richTextEditor.module.css";
import { cn } from "@/lib/utils";
import { useMutation } from "@tanstack/react-query";
import { changeLectureProgress } from "@/apiService/LectureService";

export default function LectureDetails({
  lecture,
  lectureNumber,
}: {
  lecture: Lecture & LectureResponse;
  lectureNumber: number | null;
}) {
  const { previewUrl } = useVideo(lecture?.video?.storageKey as string);

  const { mutate: changeLectureProgressMutation } = useMutation({
    mutationFn: ({ time_spent }: { time_spent: number }) =>
      changeLectureProgress({ lectureId: lecture.id, completed: true, time_spent }),
  });

  return (
    <div className='w-full'>
      <Player
        src={previewUrl || (lecture?.video as string)}
        onEnded={(e) =>
          lecture?.video &&
          changeLectureProgressMutation({ time_spent: (e.target as HTMLVideoElement).currentTime })
        }
      />

      <div>
        <h1 className='text-2xl mt-4'>
          {lectureNumber}.{lecture?.title}
        </h1>
        <span className='text-sm text-muted-foreground mt-1'>
          <span className='flex items-center gap-2 text-xs'>
            <p className='text-muted-foreground'>Last updated:</p>
            <p className='text-black'>{moment(lecture?.updatedAt).format("MMM DD, YYYY")}</p>
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
          <div className={cn(styles.editorContainer, "mt-2")}>
            <p>{lecture?.description && HtmlParser(lecture.description)}</p>
          </div>
        </TabsContent>

        <TabsContent value='attachments'>
          <h1 className='text-lg font-bold'>Attachments</h1>
          <p>{lecture?.attachments?.name}</p>
        </TabsContent>
      </Tabs>
    </div>
  );
}
