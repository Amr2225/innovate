import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import React from "react";
import moment from "moment";
import { Check, X } from "lucide-react";
import Link from "next/link";

export default function AssignmentCard({
  id,
  title,
  dueDate,
  startDate,
  hasSubmitted,
}: {
  id: string;
  title: string;
  dueDate: Date;
  startDate: Date;
  hasSubmitted: boolean;
}) {
  return (
    <div className='w-full h-full border border-neutral-200 rounded-md py-2'>
      {/* <span className='w-[200px] block h-[100px] bg-white rounded-full' /> */}
      <div className='flex flex-col items-start justify-center px-3 py-1'>
        <h4 className='font-bold text-sm'>{title}</h4>
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
          <Link href={`/student/assessment/${id}`}>View Assignment</Link>
        </Button>
      </div>
    </div>
  );
}
