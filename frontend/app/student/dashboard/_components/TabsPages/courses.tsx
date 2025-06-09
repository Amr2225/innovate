import React from "react";
import {
  Select,
  SelectValue,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from "@/components/ui/select";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";

import CourseCard from "../courseCard";

export default function CousresSection() {
  return (
    <div>
      <h1 className='text-xl font-bold mt-3'>Courses (20)</h1>
      <div className='grid grid-cols-5 items-center gap-4 mb-5'>
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
        <CourseCard />
        <CourseCard />
        <CourseCard />
        <CourseCard />
        <CourseCard />
      </div>
    </div>
  );
}
