import React, { useState } from "react";

import CustomDialog from "@/components/CustomDialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { DialogFooter } from "@/components/ui/dialog";
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { Plus } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { addAssessmentSchema, AddAssessmentSchema } from "@/schema/addAssessmentSchema";
import { getCourses } from "@/apiService/courseService";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";

export default function AddAssessment() {
  const [open, setOpen] = useState(false);

  const form = useForm<AddAssessmentSchema>({
    resolver: zodResolver(addAssessmentSchema),
    defaultValues: {
      title: "",
      course: "",
      type: "Assignment",
      due_date: new Date(),
      total_grade: 0,
    },
  });

  const { data: courses, isLoading: isLoadingCourses } = useQuery({
    queryKey: ["institution-courses"],
    queryFn: () => getCourses({ page_size: 1000 }),
  });

  return (
    <CustomDialog
      title='Create New Assessment'
      description='Create a new assessment for your courses'
      open={open}
      setOpen={setOpen}
      trigger={
        <Button className='gap-1'>
          <Plus size={16} />
          Add Assessment
        </Button>
      }
    >
      <Form {...form}>
        <form onSubmit={form.handleSubmit(() => {})}>
          <FormField
            control={form.control}
            name='title'
            render={({ field }) => (
              <FormItem>
                <FormLabel className='after:content-["*"] after:ml-0.5 after:text-red-500'>
                  Title
                </FormLabel>
                <FormControl>
                  <Input placeholder='Assessment Title' {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name='course'
            render={({ field }) =>
              isLoadingCourses ? (
                <FormItem className='w-full'>
                  <Skeleton className='w-full h-[40px]' />
                </FormItem>
              ) : (
                <FormItem>
                  <FormLabel className='after:content-["*"] after:ml-0.5 after:text-red-500'>
                    Course
                  </FormLabel>
                  <FormControl>
                    <Select
                      onValueChange={(value) => field.onChange(value === "null" ? "" : value)}
                      value={field.value || "null"}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder='Select a prerequisite course' />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className='max-h-[300px] overflow-y-scroll '>
                        {/* <SelectItem
                          value='null'
                          className='hover:cursor-pointer hover:bg-neutral-100'
                        >
                          None
                        </SelectItem> */}
                        {courses?.data.map((course) => (
                          <SelectItem
                            key={course.id}
                            value={course.id}
                            className='hover:cursor-pointer hover:bg-neutral-100'
                          >
                            {course.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )
            }
          />

          <FormField
            control={form.control}
            name='type'
            render={({ field }) => (
              <FormItem>
                <FormLabel>Type</FormLabel>
                <FormControl>
                  <Select onValueChange={(value) => field.onChange(value)} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder='Select a type' />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value='Assignment'>Assignment</SelectItem>
                      <SelectItem value='Quiz'>Quiz</SelectItem>
                      <SelectItem value='Exam'>Exam</SelectItem>
                    </SelectContent>
                  </Select>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name='total_grade'
            render={({ field }) => (
              <FormItem>
                <FormLabel>Total Grade</FormLabel>
                <FormControl>
                  <Input type='number' placeholder='Total Grade' {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className='grid grid-cols-2 items-center gap-4'>
            <FormField
              control={form.control}
              name='start_date'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Start Date</FormLabel>
                  <FormControl>
                    <Input type='date' {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name='due_date'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Due Date</FormLabel>
                  <FormControl>
                    <Input type='date' {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </form>
      </Form>
      <div className='grid gap-4 py-4'>
        <div className='grid grid-cols-4 items-center gap-4'>
          <label htmlFor='assessmentTitle' className='text-right'>
            Title
          </label>
          <Input id='assessmentTitle' placeholder='e.g. Midterm Exam' className='col-span-3' />
        </div>
        <div className='grid grid-cols-4 items-center gap-4'>
          <label htmlFor='courseSelect' className='text-right'>
            Course
          </label>
          <Input id='courseSelect' placeholder='Select course' className='col-span-3' />
        </div>
        <div className='grid grid-cols-4 items-center gap-4'>
          <label htmlFor='assessmentType' className='text-right'>
            Type
          </label>
          <Input
            id='assessmentType'
            placeholder='e.g. Exam, Quiz, Assignment'
            className='col-span-3'
          />
        </div>
        <div className='grid grid-cols-4 items-center gap-4'>
          <label htmlFor='dueDate' className='text-right'>
            Due Date
          </label>
          <Input id='dueDate' type='date' className='col-span-3' />
        </div>
        <div className='grid grid-cols-4 items-center gap-4'>
          <label htmlFor='totalMarks' className='text-right'>
            Total Marks
          </label>
          <Input id='totalMarks' type='number' placeholder='e.g. 100' className='col-span-3' />
        </div>
      </div>
      <DialogFooter>
        <Button type='submit'>Create Assessment</Button>
      </DialogFooter>
    </CustomDialog>
  );
}
