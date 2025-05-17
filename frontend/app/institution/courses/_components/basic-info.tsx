"use client";
import React, { useState } from "react";
import { useForm } from "react-hook-form";

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useQuery, useMutation } from "@tanstack/react-query";
import { createCourse, getCourses } from "@/apiService/courseService";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Course } from "@/types/course.type";
import { getMembers } from "@/apiService/institutionService";

export default function BasInfoForm() {
  const [courseId, setCourseId] = useState<string | null>(null);
  const form = useForm({
    defaultValues: {
      name: "",
      description: "",
      prerequisite_course: null,
      instructors: null,
      semester: 0,
      credit_hours: 0,
      total_grade: 0,
    },
  });

  const { data: courses, isLoading: isLoadingCourses } = useQuery({
    queryKey: ["prerequisite-courses"],
    queryFn: getCourses,
  });

  const { data: instructors, isLoading: isLoadingInstructors } = useQuery({
    queryKey: ["instructors"],
    queryFn: async () => {
      const res = await getMembers(1, 1000, "Teacher");
      return res.data;
    },
  });

  const { mutate: createCourseMutation } = useMutation({
    mutationFn: (course: Course) => createCourse(course),
    onSuccess: (data) => {
      toast.success("Course created successfully");
      console.log(data);
      setCourseId(data.id);
    },
    onError: () => {
      toast.error("Failed to create course");
    },
  });

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const handleNext = (data: any) => {
    console.log(data);
    const courseData: Course = {
      ...data,
      instructors: [data.instructors],
    };
    createCourseMutation(courseData);
  };

  return (
    <div className='mt-5'>
      <Form {...form}>
        {courseId}
        <form onSubmit={form.handleSubmit(handleNext)} className='space-y-4'>
          <FormField
            control={form.control}
            name='name'
            render={({ field }) => (
              <FormItem>
                <FormLabel>Course Name</FormLabel>
                <FormControl>
                  <Input placeholder='Course Name' {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name='description'
            render={({ field }) => (
              <FormItem>
                <FormLabel>Course Description</FormLabel>
                <FormControl>
                  <Input placeholder='Course Description' {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name='prerequisite_course'
            render={({ field }) =>
              isLoadingCourses ? (
                <FormItem className='w-full'>
                  <Loader2 className='size-5 animate-spin text-primary' />
                </FormItem>
              ) : (
                <FormItem className='w-full'>
                  <FormLabel>Prerequisite Course</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value ?? undefined}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder='Select a prerequisite course' />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value={"none"}>None</SelectItem>
                      {courses?.map((course) => (
                        <SelectItem key={course.id} value={course.id}>
                          {course.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )
            }
          />

          <FormField
            control={form.control}
            name='instructors'
            render={({ field }) =>
              isLoadingInstructors ? (
                <FormItem className='w-full'>
                  <Loader2 className='size-5 animate-spin text-primary' />
                </FormItem>
              ) : (
                <FormItem className='w-full'>
                  <FormLabel>Instructor</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value ?? undefined}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder='Select a instructor' />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value={"none"}>None</SelectItem>
                      {instructors?.map((instructor) => (
                        <SelectItem key={instructor.id} value={instructor?.id ?? ""}>
                          {instructor.full_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )
            }
          />

          <div className='flex justify-between items-center gap-5'>
            <FormField
              control={form.control}
              name='semester'
              render={({ field }) => (
                <FormItem className='w-full'>
                  <FormLabel>Semester</FormLabel>
                  <FormControl>
                    <Input
                      type='number'
                      min={1}
                      max={8}
                      placeholder='Enter Semester For this course'
                      {...field}
                      onChange={(e) => field.onChange(Number(e.target.value) || "")}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name='credit_hours'
              render={({ field }) => (
                <FormItem className='w-full'>
                  <FormLabel>Credit Hours</FormLabel>
                  <FormControl>
                    <Input
                      type='number'
                      min={1}
                      max={7}
                      placeholder='Enter credit hours'
                      {...field}
                      onChange={(e) => field.onChange(Number(e.target.value) || "")}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name='total_grade'
              render={({ field }) => (
                <FormItem className='w-full'>
                  <FormLabel>Total Grade</FormLabel>
                  <FormControl>
                    <Input
                      type='number'
                      min={1}
                      max={100}
                      placeholder='Enter total grade'
                      {...field}
                      onChange={(e) => field.onChange(Number(e.target.value) || "")}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <div className='flex justify-between items-center mt-10 '>
            <Button type='button' variant={"secondary"}>
              Cancel
            </Button>
            <Button type='submit'>Save & Next</Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
