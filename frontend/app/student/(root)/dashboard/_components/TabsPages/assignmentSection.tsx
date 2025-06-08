"use client";
import React from "react";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";

import {
  Select,
  SelectValue,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from "@/components/ui/select";

import AssignmentCard from "../assignmentCard";

import { useQuery } from "@tanstack/react-query";
import { getAssessment } from "@/apiService/assessmentService";
import Loader from "@/components/Loader";

export default function AssignmentSection() {
  const { data: assignments, isLoading } = useQuery({
    queryKey: ["assignments"],
    queryFn: getAssessment,
  });

  if (isLoading) return <Loader />;

  return (
    <div>
      <h1 className='text-xl font-bold mt-3'>Assignments (10)</h1>
      <div className='grid grid-cols-5 items-center gap-4 mb-8'>
        <div className='col-span-2'>
          <Label htmlFor='search'>Search:</Label>
          <Input id='search' placeholder='Search in your courses..' />
        </div>

        <div>
          <Label>Sort by:</Label>
          <Select defaultValue='latest'>
            <SelectTrigger className='w-full'>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='latest'>Latest</SelectItem>
              <SelectItem value='earliest'>Earliest</SelectItem>
              <SelectItem value='alphabetical'>Alphabetical</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor='sort'>Status:</Label>
          <Select defaultValue='latest'>
            <SelectTrigger className='w-full'>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='latest'>Latest</SelectItem>
              <SelectItem value='earliest'>Earliest</SelectItem>
              <SelectItem value='alphabetical'>Alphabetical</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor='sort'>Teacher:</Label>
          <Select defaultValue='latest'>
            <SelectTrigger className='w-full'>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='latest'>Latest</SelectItem>
              <SelectItem value='earliest'>Earliest</SelectItem>
              <SelectItem value='alphabetical'>Alphabetical</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className='grid grid-cols-4 gap-4 pb-5'>
        {assignments?.data.map((assignment) => (
          <AssignmentCard
            id={assignment.id}
            key={assignment.id}
            title={assignment.title}
            dueDate={assignment.due_date}
            startDate={assignment.start_date!}
            hasSubmitted={assignment.has_submitted}
            courseName={assignment.course}
          />
        ))}
      </div>
    </div>
  );
}
