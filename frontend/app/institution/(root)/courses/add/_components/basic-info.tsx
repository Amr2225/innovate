"use client";
import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

// Components
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
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

// Query
import { useQuery } from "@tanstack/react-query";

// Services
import { getCourses } from "@/apiService/courseService";
import { getMembers } from "@/apiService/institutionService";

// Icons
import { Loader2 } from "lucide-react";

// Types
import { Course } from "@/types/course.type";
import { createCourseStore } from "@/store/courseStore";

// Store
// importcreateCourseStore,  { useCourseStore } from "@/store/courseStore";

const formSchema = z.object({
  name: z.string().min(1, "Course name is required"),
  description: z.string().min(1, "Description is required"),
  prerequisite_course: z.string().nullable(),
  instructors: z.array(z.string()).min(1, "At least one instructor is required"),
  semester: z.number({ message: "Semester is required" }).min(1, "Semester must be at least 1"),
  credit_hours: z
    .number({ message: "Credit hours is required" })
    .min(1, "Credit hours must be at least 1"),
  total_grade: z
    .number({ message: "Total grade is required" })
    .min(1, "Total grade must be at least 1"),
});

export default function BasInfoForm() {
  const useCourseStore = createCourseStore("new");
  const { addCourse } = useCourseStore();

  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: useCourseStore.getState().course?.name || "",
      description: useCourseStore.getState().course?.description || "",
      prerequisite_course: useCourseStore.getState().course?.prerequisite_course || null,
      instructors: useCourseStore.getState().course?.instructors || [],
      semester: useCourseStore.getState().course?.semester || 0,
      credit_hours: useCourseStore.getState().course?.credit_hours || 0,
      total_grade: useCourseStore.getState().course?.total_grade || 0,
    },
    mode: "onChange",
  });

  const { data: courses, isLoading: isLoadingCourses } = useQuery({
    queryKey: ["prerequisite-courses"],
    queryFn: () => getCourses({ page_size: 1000 }),
  });

  const { data: instructors, isLoading: isLoadingInstructors } = useQuery({
    queryKey: ["instructors"],
    queryFn: async () => {
      const res = await getMembers(1, 1000, "Teacher");
      return res.data;
    },
  });

  const handleNext = (data: {
    name: string;
    description: string;
    prerequisite_course: string | null;
    instructors: string[];
    semester: number;
    credit_hours: number;
    total_grade: number;
  }) => {
    console.log(data);
    const courseData: Course = {
      id: "", // Not used but required for type check only
      ...data,
      instructors: data.instructors,
    };
    addCourse(courseData);
  };

  return (
    <div className='mt-5'>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleNext)} className='space-y-4' id='course-form'>
          <FormField
            control={form.control}
            name='name'
            render={({ field }) => (
              <FormItem>
                <FormLabel className="after:content-['*'] after:ml-0.5 after:text-red-500">
                  Course Name
                </FormLabel>
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
                <FormLabel className="after:content-['*'] after:ml-0.5 after:text-red-500">
                  Course Description
                </FormLabel>
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
                  <Select
                    onValueChange={(value) => field.onChange(value === "null" ? null : value)}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder='Select a prerequisite course' />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value='null'>None</SelectItem>
                      {courses?.data.map((course) => (
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
                  <FormLabel className="after:content-['*'] after:ml-0.5 after:text-red-500">
                    Instructor
                  </FormLabel>
                  <FormControl>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant='outline' className='w-full justify-between'>
                          Select Instructors
                          <span className='ml-2 opacity-70'>
                            {Array.isArray(field.value) && field.value.length > 0
                              ? `${field.value.length} selected`
                              : "None"}
                          </span>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent
                        className='max-h-full overflow-auto'
                        sideOffset={4}
                        style={{ width: "var(--radix-dropdown-menu-trigger-width)" }}
                      >
                        <DropdownMenuLabel>Select Instructors</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        {instructors?.map((instructor) => (
                          <DropdownMenuCheckboxItem
                            key={instructor.id}
                            checked={
                              Array.isArray(field.value) &&
                              field.value.includes(instructor.id || "")
                            }
                            onCheckedChange={(checked) => {
                              const currentValues = Array.isArray(field.value) ? field.value : [];
                              if (checked) {
                                field.onChange([...currentValues, instructor.id]);
                              } else {
                                field.onChange(currentValues.filter((id) => id !== instructor.id));
                              }
                            }}
                          >
                            {instructor.full_name}
                          </DropdownMenuCheckboxItem>
                        ))}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </FormControl>
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
                  <FormLabel className="after:content-['*'] after:ml-0.5 after:text-red-500">
                    Semester
                  </FormLabel>
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
                  <FormLabel className="after:content-['*'] after:ml-0.5 after:text-red-500">
                    Credit Hours
                  </FormLabel>
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
                  <FormLabel className="after:content-['*'] after:ml-0.5 after:text-red-500">
                    Total Grade
                  </FormLabel>
                  <FormControl>
                    <Input
                      type='number'
                      min={1}
                      max={300}
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

          <div className='flex justify-end items-center mt-10 '>
            {/* <Button type='button' variant={"secondary"}>
              Cancel
            </Button> */}
            <Button type='submit'>Save & Next</Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
