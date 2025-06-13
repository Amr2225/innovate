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

import AssignmentCard from "../assessmentCard";

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

export default function AssignmentSection() {
  const [globalFilter, setGlobalFilter] = useState<GlobalFilter>({});
  const [filter] = useDebounce(globalFilter, 500);

  const { data: assignments, isLoading } = useQuery({
    queryKey: ["assignments", filter],
    queryFn: () => getAssessment({ pageParam: 1, page_size: 1000, type: "Assignment", ...filter }),
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
        <h1 className='text-xl font-bold mt-3'>Assignments ({dashboardData?.assignment_count})</h1>
      )}
      <div className='grid grid-cols-5 items-center gap-4 mb-8'>
        <div className='col-span-2'>
          <Label htmlFor='search'>Search:</Label>
          <Input
            id='search'
            value={globalFilter.title || ""}
            onChange={(e) => setGlobalFilter({ ...globalFilter, title: e.target.value })}
            placeholder='Search in your courses..'
          />
        </div>

        <div>
          <Label htmlFor='sort'>Status:</Label>
          <Select
            defaultValue='all'
            onValueChange={(value) =>
              setGlobalFilter({
                ...globalFilter,
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
                ...globalFilter,
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
          assignments?.data.map((assignment) => (
            <AssignmentCard
              id={assignment.id}
              key={assignment.id}
              title={assignment.title}
              dueDate={assignment.due_date}
              startDate={assignment.start_date!}
              hasSubmitted={assignment.has_submitted}
              courseName={assignment.course}
            />
          ))
        )}
      </div>
    </div>
  );
}
