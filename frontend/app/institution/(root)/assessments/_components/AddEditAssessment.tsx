import React, { Dispatch, SetStateAction, useState } from "react";

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

import { Loader2, Plus } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { addAssessmentSchema, AddAssessmentSchema } from "@/schema/addAssessmentSchema";
import { getCourses } from "@/apiService/courseService";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { DateTimePicker } from "@/components/date-picker";
import { createAssessment, updateAssessment } from "@/apiService/assessmentService";
import { toast } from "sonner";
import { Assessment } from "@/types/assessment.type";

interface AddEditAssessmentProps {
  assessment?: Assessment;
  isDialogOpen?: boolean;
  setIsDialogOpen?: Dispatch<SetStateAction<string | null>>;
  courseId?: string | null;
}

export default function AddEditAssessment({
  assessment,
  isDialogOpen = false,
  setIsDialogOpen,
  courseId,
}: AddEditAssessmentProps) {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(isDialogOpen || typeof courseId === "string");

  const handleDialogOpenChange = (newOpenState: boolean) => {
    setOpen(newOpenState);
    if (setIsDialogOpen) {
      if (open) setIsDialogOpen(null);
      else setIsDialogOpen(assessment?.id || null);
    }
  };

  const { mutate: createAssessmentMutation, isPending: isCreatingAssessment } = useMutation({
    mutationFn: (assessment: AddAssessmentSchema) =>
      createAssessment({
        courseId: assessment.course,
        title: assessment.title,
        type: assessment.type,
        due_date: assessment.due_date,
        start_date: assessment.start_date,
        // grade: assessment.total_grade,
      }),
    onSuccess: () => {
      toast.success("Assessment created successfully");
      queryClient.invalidateQueries({ queryKey: ["institution-assessments"] });
      form.reset();
    },
    onError: (error) => {
      toast.error(error.message);
    },
    onMutate: () => {
      setOpen(false);
    },
  });

  const { mutate: updateAssessmentMutation, isPending: isUpdatingAssessment } = useMutation({
    mutationFn: (updatedAssessment: AddAssessmentSchema) =>
      updateAssessment({
        courseId: updatedAssessment.course,
        id: assessment?.id as string,
        title: updatedAssessment.title,
        type: updatedAssessment.type,
        due_date: updatedAssessment.due_date,
        start_date: updatedAssessment.start_date,
        // grade: updatedAssessment.total_grade,
      }),
    onSuccess: () => {
      toast.success("Assessment updated successfully");
      queryClient.invalidateQueries({ queryKey: ["institution-assessments"] });
      form.reset();
      setOpen(false);
      setIsDialogOpen?.(null);
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const form = useForm<AddAssessmentSchema>({
    resolver: zodResolver(addAssessmentSchema),
    defaultValues: {
      title: assessment?.title || "",
      course: assessment?.courseId || courseId || "",
      type: assessment?.type || "Assignment",
      due_date: assessment?.due_date ? new Date(assessment.due_date) : new Date(),
      start_date: assessment?.start_date ? new Date(assessment.start_date) : null,
    },
  });

  const { data: courses, isLoading: isLoadingCourses } = useQuery({
    queryKey: ["institution-courses"],
    queryFn: () => getCourses({ page_size: 1000 }),
  });

  return (
    <CustomDialog
      title={assessment ? `Edit Assessment ${assessment.title}` : "Create New Assessment"}
      description={
        assessment
          ? `Edit the assessment details ${assessment.title}`
          : "Create a new assessment for your courses"
      }
      open={open}
      setOpen={handleDialogOpenChange}
      trigger={
        !assessment && (
          <Button className='gap-1' disabled={isCreatingAssessment}>
            {isCreatingAssessment ? (
              <Loader2 className='animate-spin' size={16} />
            ) : (
              <>
                <Plus size={16} />
                Add Assessment
              </>
            )}
          </Button>
        )
      }
    >
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit((data) => {
            if (assessment) updateAssessmentMutation(data);
            else createAssessmentMutation(data);
          })}
          className='space-y-2'
        >
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
                <FormLabel className='after:content-["*"] after:ml-0.5 after:text-red-500'>
                  Type
                </FormLabel>
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

          <div className='grid grid-cols-2 items-center gap-4'>
            <FormField
              control={form.control}
              name='start_date'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Start Date</FormLabel>
                  <FormControl>
                    <DateTimePicker date={field.value || undefined} setDate={field.onChange} />
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
                  <FormLabel className='after:content-["*"] after:ml-0.5 after:text-red-500'>
                    Due Date
                  </FormLabel>
                  <FormControl>
                    <DateTimePicker date={field.value} setDate={field.onChange} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          <DialogFooter className='mt-5 !flex !flex-row !justify-between'>
            <h6 className='text-xs text-muted-foreground after:content-["*"] after:ml-0.5 after:text-red-500'>
              Required fields are marked with
            </h6>

            <Button type='submit' disabled={isUpdatingAssessment}>
              {isUpdatingAssessment ? (
                <Loader2 className='animate-spin' size={16} />
              ) : (
                <>
                  <Plus size={16} />
                  {assessment ? "Update Assessment" : "Create Assessment"}
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </Form>
    </CustomDialog>
  );
}
