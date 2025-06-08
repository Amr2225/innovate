"use client";
import React from "react";
import MaterialsContainer from "@/components/addMaterials/materialsContainer";
import { Button } from "@/components/ui/button";
import { useParams } from "next/navigation";
import { useEditCourse } from "@/queryHooks/useEditCourse";
import { Loader2 } from "lucide-react";

export default function AddMaterials() {
  const { courseId } = useParams();
  const { UploadCourse, isCreating } = useEditCourse(courseId as string);

  return (
    <div className='p-5'>
      <div className='flex justify-between items-center'>
        <h1 className='text-3xl font-bold'>Course Curriculum</h1>
        <div>
          <Button variant='default' onClick={UploadCourse} disabled={isCreating}>
            {isCreating ? <Loader2 className='size-4 animate-spin' /> : "Upload"}
          </Button>
          <Button variant='link'>Save & Preview</Button>
        </div>
      </div>
      <MaterialsContainer />
    </div>
  );
}
