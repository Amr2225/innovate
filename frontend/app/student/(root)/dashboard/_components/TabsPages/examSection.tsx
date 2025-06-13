"use client";
import React, { useState } from "react";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";

import {
  Select,
  SelectValue,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from "@/components/ui/select";

import AssessmentCard from "../assessmentCard";
import { useQuery } from "@tanstack/react-query";
import { getAssessment } from "@/apiService/assessmentService";
import { studentAnalytics } from "@/apiService/analytics";
import { Skeleton } from "@/components/ui/skeleton";
import { useDebounce } from "use-debounce";
import { DatePickerRange } from "@/components/date-picker";

interface GlobalFilter {
  title?: string;
  has_submitted?: boolean;
  due_date_after?: string;
  due_date_before?: string;
  start_date_after?: string;
  start_date_before?: string;
}

export default function ExamSection() {
  const [globalFilter, setGlobalFilter] = useState<GlobalFilter>({});
  const [filter] = useDebounce(globalFilter, 500);

  const { data: exams, isLoading } = useQuery({
    queryKey: ["exams", filter],
    queryFn: () => getAssessment({ pageParam: 1, page_size: 10000, type: "Exam", ...filter }),
  });

  const { data: dashboardData, isLoading: dashboardLoading } = useQuery({
    queryKey: ["student-dashboard"],
    queryFn: () => studentAnalytics(),
  });

  return (
    <div>
      {dashboardLoading ? (
        <Skeleton className='w-full h-[50px]' />
      ) : (
        <h1 className='text-xl font-bold mt-3'>Exams ({dashboardData?.exam_count})</h1>
      )}
      <div className='grid grid-cols-5 items-center gap-4 mb-8'>
        <div className='col-span-2'>
          <Label htmlFor='search'>Search:</Label>
          <Input
            id='search'
            value={globalFilter.title || ""}
            onChange={(e) => setGlobalFilter({ title: e.target.value })}
            placeholder='Search in your courses..'
          />
        </div>

        <div>
          <Label htmlFor='sort'>Status:</Label>
          <Select
            defaultValue='all'
            onValueChange={(value) =>
              setGlobalFilter({
                has_submitted: value === "all" ? undefined : value === "true",
              })
            }
          >
            <SelectTrigger className='w-full'>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='all'>All</SelectItem>
              <SelectItem value='true'>Submitted</SelectItem>
              <SelectItem value='false'>Not Submitted</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor='start_date'>Start Date:</Label>
          <DatePickerRange
            date={{
              from: globalFilter.start_date_after
                ? new Date(globalFilter.start_date_after)
                : undefined,
              to: globalFilter.start_date_before
                ? new Date(globalFilter.start_date_before)
                : undefined,
            }}
            setDate={(value) =>
              setGlobalFilter({
                start_date_after: value.from?.toISOString(),
                start_date_before: value.to?.toISOString(),
              })
            }
          />
        </div>

        <div>
          <Label htmlFor='due_date'>Due Date:</Label>
          <DatePickerRange
            date={{
              from: globalFilter.due_date_after ? new Date(globalFilter.due_date_after) : undefined,
              to: globalFilter.due_date_before ? new Date(globalFilter.due_date_before) : undefined,
            }}
            setDate={(value) =>
              setGlobalFilter({
                due_date_after: value.from?.toISOString(),
                due_date_before: value.to?.toISOString(),
              })
            }
          />
        </div>
      </div>

      <div className='grid grid-cols-4 gap-4 pb-5'>
        {isLoading ? (
          <>
            <Skeleton className='w-full h-[100px]' />
            <Skeleton className='w-full h-[100px]' />
            <Skeleton className='w-full h-[100px]' />
            <Skeleton className='w-full h-[100px]' />
          </>
        ) : (
          exams?.data.map((exam) => (
            <AssessmentCard
              id={exam.id}
              key={exam.id}
              title={exam.title}
              dueDate={exam.due_date}
              startDate={exam.start_date!}
              hasSubmitted={exam.has_submitted}
              courseName={exam.course}
            />
          ))
        )}
      </div>
    </div>
  );
}
