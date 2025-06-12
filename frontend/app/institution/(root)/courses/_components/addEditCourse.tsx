import { useState, SetStateAction, Dispatch } from "react";

import { DialogFooter } from "@/components/ui/dialog";
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Edit, Loader2, Plus } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

// Types
import { courseSchema, CourseSchema } from "@/schema/courseSchema";

// Local Components
import CustomDialog from "@/components/CustomDialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useQuery } from "@tanstack/react-query";

// API
import { createCourse, getCourses, updateCourse } from "@/apiService/courseService";
import { Skeleton } from "@/components/ui/skeleton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuCheckboxItem,
} from "@/components/ui/dropdown-menu";
import { getMembers } from "@/apiService/institutionService";
import { toast } from "sonner";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Course } from "@/types/course.type";

export default function AddEditCourse({
  course,
  isDialogOpen = false,
  setIsDialogOpen,
}: {
  course?: Course;
  isDialogOpen?: boolean;
  setIsDialogOpen?: Dispatch<SetStateAction<string | null>>;
}) {
  const [isOpen, setIsOpen] = useState(isDialogOpen);
  const [selectOpen, setSelectOpen] = useState(false);
  const queryClient = useQueryClient();

  const handleDialogOpenChange = (newOpenState: boolean) => {
    setIsOpen(newOpenState);
    if (setIsDialogOpen) {
      if (isOpen) setIsDialogOpen(null);
      else setIsDialogOpen(course?.id || null);
    }
  };

  const handleSelectOpenChange = (newOpenState: boolean) => {
    setSelectOpen(newOpenState);
    setTimeout(() => {
      document.body.style.pointerEvents = "";
    }, 100);
  };

  const form = useForm<CourseSchema>({
    resolver: zodResolver(courseSchema),
    defaultValues: {
      name: course?.name || "",
      description: course?.description || "",
      prerequisite_course: course?.prerequisite_course_detail?.id || null,
      instructors: course?.instructors || [],
      semester: course?.semester || 0,
      credit_hours: course?.credit_hours || 0,
      total_grade: course?.total_grade || 0,
    },
  });

  const { data: courses, isLoading: isLoadingCourses } = useQuery({
    queryKey: ["prerequisite-courses"],
    queryFn: () => getCourses({ page_size: 1000 }),
  });

  const { data: instructors, isLoading: isLoadingInstructors } = useQuery({
    queryKey: ["institution-instructors"],
    queryFn: async () => {
      const res = await getMembers({ pageParam: 1, pageSize: 1000, role: "Teacher" });
      return res.data;
    },
  });

  const { mutate: createCourseMutation, isPending: isCreatingCourse } = useMutation({
    mutationFn: (course: Omit<Course, "id">) => createCourse(course),
    onSuccess: () => {
      toast.success("Course created successfully");
      queryClient.invalidateQueries({ queryKey: ["institution-courses"] });
      form.reset();
    },
    onError: (error) => {
      toast.error(error.message);
    },
    onMutate: () => {
      setIsOpen(false);
    },
  });

  const { mutate: updateCourseMutation, isPending: isUpdatingCourse } = useMutation({
    mutationFn: (course: Course) => updateCourse(course),
    onSuccess: () => {
      toast.success("Course updated successfully");
      queryClient.invalidateQueries({ queryKey: ["institution-courses"] });
      form.reset();
      setIsOpen(false);
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  return (
    <CustomDialog
      title={course ? "Edit Course" : "Add New Course"}
      description={course ? "Edit the course details" : "Create a new course for your institution."}
      trigger={
        !course && (
          <Button
            className='gap-1'
            variant={course ? "link" : "default"}
            disabled={isCreatingCourse}
          >
            {isCreatingCourse ? (
              <Loader2 className='animate-spin' size={16} />
            ) : (
              <>
                {course ? <Edit className='mr-2 h-4 w-4' /> : <Plus size={16} />}
                {course ? "Edit Course" : "Add Course"}
              </>
            )}
          </Button>
        )
      }
      open={isOpen}
      setOpen={handleDialogOpenChange}
    >
      <Form {...form}>
        <form
          className='space-y-2'
          onSubmit={form.handleSubmit((data) => {
            if (course) updateCourseMutation({ ...data, id: course.id });
            else createCourseMutation(data);
          })}
        >
          <FormField
            control={form.control}
            name='name'
            render={({ field }) => (
              <FormItem>
                <FormLabel className='after:content-["*"] after:ml-0.5 after:text-red-500'>
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
                  <Skeleton className='w-full h-[40px]' />
                </FormItem>
              ) : (
                <FormItem className='w-full'>
                  <FormLabel>Prerequisite Course</FormLabel>
                  <Select
                    open={selectOpen}
                    onOpenChange={handleSelectOpenChange}
                    onValueChange={(value) => field.onChange(value === "null" ? null : value)}
                    value={field.value || "null"}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder='Select a prerequisite course' />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent className='max-h-[300px] overflow-y-scroll '>
                      <SelectItem
                        value='null'
                        className='hover:cursor-pointer hover:bg-neutral-100'
                      >
                        None
                      </SelectItem>
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
                  <Skeleton className='w-full h-[40px]' />
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
                            className='hover:cursor-pointer hover:bg-neutral-100'
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

          <DialogFooter className='mt-5 !flex !flex-row !justify-between'>
            <h6 className='text-xs text-muted-foreground after:content-["*"] after:ml-0.5 after:text-red-500'>
              Required fields are marked with
            </h6>
            <Button type='submit' disabled={isUpdatingCourse}>
              {isUpdatingCourse ? (
                <Loader2 className='animate-spin' size={16} />
              ) : (
                <>{course ? "Update Course" : "Create Course"}</>
              )}
            </Button>
          </DialogFooter>
        </form>
      </Form>
    </CustomDialog>
  );
}
