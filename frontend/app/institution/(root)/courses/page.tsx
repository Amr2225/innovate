"use client";

import React, { useState, useMemo } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Search,
  Plus,
  MoreVertical,
  FileText,
  Edit,
  Trash,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  NotebookPen,
} from "lucide-react";
import { useInfiniteQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useDebounce } from "use-debounce";
import { Course } from "@/types/course.type";
import { deleteCourse, getCourses, updateCourse } from "@/apiService/courseService";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import Link from "next/link";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";

// Local Components
import AddEditCourse from "./_components/addEditCourse";
import { toast } from "sonner";
import { useBreadcrumb } from "@/context/breadcrumbsContext";
import { useAuth } from "@/hooks/useAuth";

interface GlobalFilter {
  name?: string;
  instructor?: string;
}

interface CourseResponse extends Course {
  students_count?: number;
  is_active: boolean;
}

// Replace the EditableStatusCell component with this new version
const EditableStatusCell: React.FC<{
  value: boolean;
  onSave: (newValue: boolean) => void;
}> = ({ value, onSave }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [editValue, setEditValue] = useState(value);

  const handleSave = () => {
    onSave(editValue);
    setIsOpen(false);
  };

  const handleCancel = () => {
    setEditValue(value);
    setIsOpen(false);
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium cursor-pointer hover:opacity-80 transition-opacity ${
            value ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"
          }`}
        >
          {value ? "Active" : "Inactive"}
        </span>
      </PopoverTrigger>
      <PopoverContent className='w-48 p-4'>
        <div className='space-y-4'>
          <RadioGroup
            value={editValue ? "active" : "inactive"}
            onValueChange={(val) => setEditValue(val === "active")}
            className='space-y-2'
          >
            <div className='flex items-center space-x-2'>
              <RadioGroupItem value='active' id='active' className='size-5' />
              <Label htmlFor='active' className='text-sm font-medium'>
                Active
              </Label>
            </div>
            <div className='flex items-center space-x-2'>
              <RadioGroupItem value='inactive' id='inactive' className='size-5' />
              <Label htmlFor='inactive' className='text-sm font-medium'>
                Inactive
              </Label>
            </div>
          </RadioGroup>
          <div className='flex justify-end gap-2 pt-2'>
            <Button size='sm' variant='ghost' onClick={handleCancel} className='h-8'>
              Cancel
            </Button>
            <Button size='sm' onClick={handleSave} className='h-8'>
              Save
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
};

export default function CoursesPage() {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState<GlobalFilter>({});
  const [debouncedFilter] = useDebounce(globalFilter, 500);
  const [currentPage, setCurrentPage] = useState(1);

  const [editCourse, setEditCourse] = useState<string | null>(null);
  const [deleteCourseId, setDeleteCourseId] = useState<string | null>(null);

  const { setNewMetadata } = useBreadcrumb();
  const { user } = useAuth();

  const queryClient = useQueryClient();

  const handleAlertDialogChange = (newOpenState: boolean, courseId: string) => {
    if (newOpenState) setDeleteCourseId(courseId);
    else setDeleteCourseId(null);
  };

  // Fetch data with useInfiniteQuery
  const {
    data,
    isLoading,
    hasNextPage,
    fetchNextPage,
    hasPreviousPage,
    fetchPreviousPage,
    isFetchingNextPage,
    isFetchingPreviousPage,
  } = useInfiniteQuery({
    queryKey: ["institution-courses", debouncedFilter, currentPage],
    queryFn: () =>
      getCourses<CourseResponse>({
        pageParam: currentPage,
        page_size: 10,
        name: globalFilter.name,
        instructor: globalFilter.instructor,
      }),
    maxPages: 1,
    initialPageParam: currentPage,
    getNextPageParam: (lastPage) => lastPage.next,
    getPreviousPageParam: (firstPage) => firstPage.previous,
  });

  // Delete course
  const { mutate: deleteCourseMutation } = useMutation({
    mutationFn: (courseId: string) => deleteCourse(courseId),
    onSuccess: () => {
      toast.success("Course deleted successfully");
      queryClient.invalidateQueries({ queryKey: ["institution-courses"] });
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const { mutate: updateCourseMutation } = useMutation({
    mutationFn: (course: CourseResponse) => updateCourse(course),
    onSuccess: () => {
      toast.success("Course updated successfully");
      queryClient.invalidateQueries({ queryKey: ["institution-courses"] });
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  // Extract courses from paginated response
  const courses = useMemo(() => data?.pages.flatMap((page) => page.data) || [], [data?.pages]);

  // Define columns for TanStack Table
  const columns: ColumnDef<Course>[] = [
    {
      accessorKey: "name",
      header: ({ column }) => (
        <div className='flex items-center space-x-1'>
          <span>Course Title</span>
          <Button
            variant='ghost'
            className='p-0 h-6 w-6'
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            <ArrowUpDown className='h-3 w-3' />
          </Button>
        </div>
      ),
      cell: ({ row }) => (
        <div>
          <p className='font-semibold'>{row.getValue("name")}</p>
          <p className='text-sm text-muted-foreground'>{row.original.description}</p>
        </div>
      ),
    },
    {
      id: "instructor",
      header: ({ column }) => (
        <div className='flex items-center space-x-1'>
          <span>Instructor</span>
          <Button
            variant='ghost'
            className='p-0 h-6 w-6'
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            <ArrowUpDown className='h-3 w-3' />
          </Button>
        </div>
      ),
      accessorFn: (row) => row.instructors_detials?.[0]?.full_name || "No instructor assigned",
      cell: ({ row }) => (
        <div className='space-y-2'>
          {row.original.instructors_detials && row.original.instructors_detials.length > 0 ? (
            row.original.instructors_detials.map((instructor) => (
              <div className='flex items-center justify-start gap-1' key={instructor.id}>
                <Avatar className='size-7'>
                  {instructor.avatar ? (
                    <AvatarImage src={instructor.avatar} />
                  ) : (
                    <AvatarFallback className='size-7 text-[12px] font-bold bg-gradient-to-br from-primary/80 to-primary text-primary-foreground'>
                      {instructor.full_name?.slice(0, 2).toUpperCase()}
                    </AvatarFallback>
                  )}
                </Avatar>
                <p className='text-sm font-medium text-neutral-700'>{instructor.full_name}</p>
              </div>
            ))
          ) : (
            <p className='text-sm font-medium text-neutral-700'>No instructor assigned</p>
          )}
        </div>
      ),
    },
    {
      id: "prerequisite_course",
      accessorFn: (row) => row.prerequisite_course_detail?.name || "No prerequisite course",
      header: ({ column }) => (
        <div className='flex items-center justify-start space-x-1'>
          <span>Prerequisite Course</span>
          <Button
            variant='ghost'
            className='p-0 h-6 w-6'
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            <ArrowUpDown className='h-3 w-3' />
          </Button>
        </div>
      ),
      cell: ({ row }) => (
        <div>
          {row.original.prerequisite_course_detail ? (
            <p className='text-sm font-medium'>{row.original.prerequisite_course_detail.name}</p>
          ) : (
            <p className='text-sm text-muted-foreground'>No prerequisite course</p>
          )}
        </div>
      ),
    },
    {
      id: "students_count",
      accessorKey: "students_count",
      header: ({ column }) => (
        <div className='flex items-center justify-center space-x-1'>
          <span>Students</span>
          <Button
            variant='ghost'
            className='p-0 h-6 w-6'
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            <ArrowUpDown className='h-3 w-3' />
          </Button>
        </div>
      ),
      cell: ({ row }) => <div className='text-center'>{row.getValue("students_count")}</div>,
    },
    {
      id: "credit_hours",
      accessorKey: "credit_hours",
      header: ({ column }) => (
        <div className='flex items-center justify-center space-x-1'>
          <span>Credit Hours</span>
          <Button
            variant='ghost'
            className='p-0 h-6 w-6'
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            <ArrowUpDown className='h-3 w-3' />
          </Button>
        </div>
      ),
      cell: ({ row }) => <div className='text-center'>{row.original.credit_hours}</div>,
    },
    {
      id: "is_active",
      accessorKey: "is_active",
      header: ({ column }) => (
        <div className='flex items-center space-x-1'>
          <span>Status</span>
          <Button
            variant='ghost'
            className='p-0 h-6 w-6'
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            <ArrowUpDown className='h-3 w-3' />
          </Button>
        </div>
      ),
      cell: ({ row }) => {
        return (
          <EditableStatusCell
            value={row.getValue("is_active")}
            onSave={(newValue) => updateCourseMutation({ ...row.original, is_active: newValue })}
          />
        );
      },
    },
    {
      id: "actions",
      header: () => (
        <div className='flex items-center space-x-1'>
          <span>Actions</span>
        </div>
      ),
      cell: ({ row }) => {
        const course = row.original;
        return (
          <div className='flex justify-start gap-2'>
            <Dialog>
              <DialogTrigger asChild>
                <Button variant='ghost' size='icon' title='Add Material'>
                  <Plus className='h-4 w-4' />
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add Material to {course.name}</DialogTitle>
                  <DialogDescription>Add course materials to {course.name}</DialogDescription>
                </DialogHeader>
                <div className='grid grid-cols-2 gap-4 py-4'>
                  <Button
                    onClick={() => setNewMetadata(course.id, course.name)}
                    variant='outline'
                    className='h-24 flex flex-col gap-2'
                    asChild
                  >
                    <Link href={`/${user?.role.toLowerCase()}/courses/${course.id}/`}>
                      <NotebookPen className='h-6 w-6' />
                      <span>Add Curriculum</span>
                    </Link>
                  </Button>
                  <Button variant='outline' className='h-24 flex flex-col gap-2' asChild>
                    <Link href={`/${user?.role.toLowerCase()}/assessments?courseId=${course.id}`}>
                      <FileText className='h-6 w-6' />
                      <span>Add Assessment</span>
                    </Link>
                  </Button>
                </div>
                <DialogFooter>
                  <Button type='button' variant='outline'>
                    Cancel
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant='ghost' size='icon'>
                  <MoreVertical className='h-4 w-4' />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align='end'>
                <DropdownMenuLabel>Actions</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {/* <DropdownMenuItem
                  onClick={() => setNewMetadata(course.id, course.name)}
                  className='cursor-pointer'
                  asChild
                >
                  <Link href={`/${user?.role.toLowerCase()}/courses/${course.id}`}>
                    <Edit className='mr-2 h-4 w-4' />
                    Add Materials
                  </Link>
                </DropdownMenuItem> */}
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => setEditCourse(course.id)}
                  className='cursor-pointer'
                >
                  <Edit className='mr-2 h-4 w-4' />
                  Edit Course
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => setDeleteCourseId(course.id)}
                  className='cursor-pointer'
                >
                  <Trash className='mr-2 h-4 w-4' />
                  Delete Course
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Dialogs */}
            {editCourse === course.id && (
              <AddEditCourse
                course={course}
                isDialogOpen={editCourse === course.id}
                setIsDialogOpen={setEditCourse}
              />
            )}

            {deleteCourseId && (
              <AlertDialog
                open={deleteCourseId === course.id}
                onOpenChange={(open) => handleAlertDialogChange(open, deleteCourseId)}
              >
                <AlertDialogTrigger asChild></AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                    <AlertDialogDescription>
                      This action cannot be undone. This will permanently delete the course and all
                      its associated data.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={() => deleteCourseMutation(course.id)}>
                      Delete
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            )}
          </div>
        );
      },
    },
  ];

  // Initialize the table
  const table = useReactTable({
    data: courses,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    state: {
      sorting,
      columnFilters,
    },
  });

  return (
    <div className='container px-4 py-8 mx-auto'>
      <div className='flex justify-between items-center mb-8'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Courses</h1>
          <p className='text-muted-foreground mt-1'>
            Manage your institution&apos;s courses and course materials
          </p>
        </div>
        <AddEditCourse />
      </div>

      <div className='flex items-center mb-6 gap-2'>
        <div className='relative flex-1 max-w-sm'>
          <Search className='absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground' />
          <Input
            placeholder='Search courses...'
            className='pl-8'
            value={globalFilter.name || ""}
            onChange={(e) => setGlobalFilter({ ...globalFilter, name: e.target.value })}
          />
        </div>
      </div>

      <div className='border rounded-lg overflow-hidden bg-card'>
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={columns.length} className='text-center py-10 h-24'>
                  Loading courses...
                </TableCell>
              </TableRow>
            ) : table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className='text-center py-10 text-muted-foreground h-24'
                >
                  No courses found. Try a different search or add a new course.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination controls */}
      <div className='flex items-center justify-between space-x-2 py-4'>
        <div className='text-sm text-muted-foreground'>
          Showing {courses.length > 0 ? 1 : 0} to {courses.length} of{" "}
          {data?.pages[0]?.total_items || 0} courses
        </div>
        <div className='flex items-center space-x-2'>
          <Button
            variant='outline'
            size='sm'
            onClick={() => {
              fetchPreviousPage();
              setCurrentPage(currentPage - 1);
            }}
            disabled={!hasPreviousPage || isFetchingPreviousPage}
          >
            <ChevronLeft className='h-4 w-4' />
            <span className='sr-only'>Previous Page</span>
          </Button>

          {data?.pages[0]?.total_pages && (
            <div className='flex items-center justify-center'>
              {Array.from({ length: Math.min(5, data.pages[0].total_pages) }, (_, i) => {
                // Show at most 5 page buttons
                let pageNumber;
                if (data.pages[0].total_pages <= 5) {
                  // If 5 or fewer pages, show all
                  pageNumber = i + 1;
                } else if (currentPage <= 3) {
                  // If on pages 1-3, show pages 1-5
                  pageNumber = i + 1;
                } else if (currentPage >= data.pages[0].total_pages - 2) {
                  // If on last 3 pages, show last 5 pages
                  pageNumber = data.pages[0].total_pages - 4 + i;
                } else {
                  // Otherwise show current page and 2 pages on each side
                  pageNumber = currentPage - 2 + i;
                }

                return (
                  <Button
                    key={pageNumber}
                    variant={currentPage === pageNumber ? "default" : "outline"}
                    size='sm'
                    onClick={() => setCurrentPage(pageNumber)}
                    className='w-9 h-9'
                  >
                    {pageNumber}
                  </Button>
                );
              })}
            </div>
          )}

          <Button
            variant='outline'
            size='sm'
            onClick={() => {
              fetchNextPage();
              setCurrentPage(currentPage + 1);
            }}
            disabled={!hasNextPage || isFetchingNextPage}
          >
            <ChevronRight className='h-4 w-4' />
            <span className='sr-only'>Next Page</span>
          </Button>
        </div>
      </div>
    </div>
  );
}
