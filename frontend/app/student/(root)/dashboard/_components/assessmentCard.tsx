import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import React from "react";
import moment from "moment";
import { Check, X } from "lucide-react";
import Link from "next/link";
import { useAssessmentNavbar } from "@/context/assessmentNavbarContext";
import { Badge } from "@/components/ui/badge";

export default function AssessmentCard({
  id,
  title,
  dueDate,
  startDate,
  hasSubmitted,
  courseName,
}: {
  id: string;
  title: string;
  dueDate: Date;
  startDate: Date;
  hasSubmitted: boolean;
  courseName: string;
}) {
  const { setCourseName, setAssessmentTitle } = useAssessmentNavbar();

  return (
    <div className='w-full h-full border border-neutral-200 rounded-md py-2'>
      <div className='flex flex-col items-start justify-center px-3 py-1'>
        <div className='flex items-center justify-between w-full'>
          <h4 className='font-bold text-sm'>{title}</h4>
          <Badge className='font-bold text-center' variant={"secondary"}>
            {courseName}
          </Badge>
        </div>
        <p className='text-sm text-gray-500'>
          <span className='font-bold'>Start Date: </span>
          {startDate ? moment(startDate).format("MMM DD, YYYY") : ""}
        </p>
        <p className='text-sm text-gray-500'>
          <span className='font-bold'>Due Date: </span>
          {dueDate ? moment(dueDate).format("MMM DD, YYYY") : ""}
        </p>
        <span className='text-sm text-gray-500 flex items-center gap-2'>
          <p className='font-bold'>Has Submitted: </p>
          {hasSubmitted ? (
            <Check className='text-green-500 size-4' />
          ) : (
            <X className='text-red-500 size-4' />
          )}
        </span>
      </div>
      <Separator />
      <div className='px-3 p-2'>
        <Button type='button' variant='default' className='w-full' asChild>
          <Link
            href={
              hasSubmitted
                ? `/student/assessment/${id}/submissionView`
                : `/student/assessment/${id}`
            }
            onClick={() => {
              setCourseName(courseName);
              setAssessmentTitle(title);
            }}
          >
            {hasSubmitted ? "View Submission" : "View Assignment"}
          </Link>
        </Button>
      </div>
    </div>
  );
}
