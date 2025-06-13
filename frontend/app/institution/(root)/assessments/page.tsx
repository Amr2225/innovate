"use client";

import React, { useMemo, useState } from "react";
import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
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
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Search,
  Plus,
  MoreVertical,
  FileText,
  Calendar,
  Edit,
  Trash,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  Loader2,
} from "lucide-react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { AssessmentResponse, getAssessment } from "@/apiService/assessmentService";
import { useDebounce } from "use-debounce";
import moment from "moment";
import AddAssessment from "./_components/AddAssessment";

interface GlobalFilter {
  type?: string;
  due_date?: string;
  title?: string;
}

const getStatus = (startDate: Date, endDate: Date) => {
  const now = new Date();
  if (startDate > now) return "Upcoming";
  if (endDate < now) return "Completed";
  return "Active";
};

export default function AssessmentsPage() {
  // Table state
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState<GlobalFilter>({});
  const [debouncedFilter] = useDebounce(globalFilter, 500);
  const [currentPage, setCurrentPage] = useState(1);

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
    queryKey: ["institution-assessments", debouncedFilter, currentPage],
    queryFn: () =>
      getAssessment({
        pageParam: currentPage,
        page_size: 10,
        type: globalFilter.type,
        due_date: globalFilter.due_date,
        title: globalFilter.title,
      }),
    maxPages: 1,
    initialPageParam: currentPage,
    getNextPageParam: (lastPage) => lastPage.next,
    getPreviousPageParam: (firstPage) => firstPage.previous,
  });

  const assessments = useMemo(() => data?.pages.flatMap((page) => page.data) || [], [data?.pages]);
  console.log(assessments);

  // Column definitions
  const columns: ColumnDef<AssessmentResponse>[] = [
    {
      accessorKey: "title",
      header: "Title",
      cell: ({ row }) => <div className='font-medium'>{row.getValue("title")}</div>,
    },
    {
      accessorKey: "course",
      header: "Course",
      cell: ({ row }) => (
        <div>
          <div className='font-medium'>{row.getValue("course")}</div>
          <div className='text-xs text-muted-foreground'>{row.original.course_description}</div>
        </div>
      ),
    },
    {
      accessorKey: "type",
      header: ({ column }) => {
        return (
          <div className='flex items-center space-x-1'>
            <span>Type</span>
            <Button
              variant='ghost'
              className='p-0 h-6 w-6'
              onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            >
              <ArrowUpDown className='h-3 w-3' />
            </Button>
          </div>
        );
      },
      filterFn: (row, id, value) => {
        return value.includes(row.getValue(id));
      },
    },
    {
      accessorKey: "start_date",
      header: ({ column }) => {
        return (
          <div className='flex items-center space-x-1'>
            <span>Start Date</span>
            <Button
              variant='ghost'
              className='p-0 h-6 w-6'
              onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            >
              <ArrowUpDown className='h-3 w-3' />
            </Button>
          </div>
        );
      },
      cell: ({ row }) => moment(row.getValue("start_date")).format("MMM DD, YYYY hh:mm A"),
      sortingFn: "datetime",
    },
    {
      accessorKey: "due_date",
      header: ({ column }) => {
        return (
          <div className='flex items-center space-x-1'>
            <span>Due Date</span>
            <Button
              variant='ghost'
              className='p-0 h-6 w-6'
              onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            >
              <ArrowUpDown className='h-3 w-3' />
            </Button>
          </div>
        );
      },
      cell: ({ row }) => moment(row.getValue("due_date")).format("MMM DD, YYYY hh:mm A"),
      sortingFn: "datetime",
    },
    {
      id: "status",
      accessorFn: (row) => getStatus(new Date(row.start_date!), new Date(row.due_date!)),
      header: ({ column }) => {
        return (
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
        );
      },
      cell: ({ row }) => {
        const status = getStatus(
          new Date(row.getValue("start_date")),
          new Date(row.getValue("due_date"))
        );
        return (
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${
              status === "Active"
                ? "bg-blue-100 text-blue-800"
                : status === "Upcoming"
                ? "bg-yellow-100 text-yellow-800"
                : status === "Completed"
                ? "bg-green-100 text-green-800"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            {status}
          </span>
        );
      },
      filterFn: (row, id, value) => {
        return value.includes(row.getValue("status"));
      },
    },
    {
      accessorKey: "grade",
      header: "Grade",
      cell: ({ row }) => row.getValue("grade"),
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const assessment = row.original;
        const status = getStatus(
          new Date(row.getValue("start_date")),
          new Date(row.getValue("due_date"))
        );
        return (
          <div className='flex justify-start gap-2'>
            <Dialog>
              <DialogTrigger asChild>
                <Button variant='ghost' size='icon' title='View Details'>
                  <FileText className='h-4 w-4' />
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>{assessment.title}</DialogTitle>
                  <DialogDescription>
                    Details for {assessment.title}: {assessment.course}
                  </DialogDescription>
                </DialogHeader>
                <div className='grid gap-4 py-4'>
                  <div className='grid grid-cols-2 items-start gap-4'>
                    <div className='space-y-1'>
                      <p className='text-sm font-medium'>Assessment Type</p>
                      <p className='text-sm text-muted-foreground'>{assessment.type}</p>
                    </div>
                    <div className='space-y-1'>
                      <p className='text-sm font-medium'>Due Date</p>
                      <p className='text-sm text-muted-foreground'>
                        {moment(assessment.due_date).format("MMM DD, YYYY")}
                      </p>
                    </div>
                    <div className='space-y-1'>
                      <p className='text-sm font-medium'>Total Marks</p>
                      <p className='text-sm text-muted-foreground'>{assessment.grade}</p>
                    </div>
                    <div className='space-y-1'>
                      <p className='text-sm font-medium'>Status</p>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          status === "Active"
                            ? "bg-blue-100 text-blue-800"
                            : status === "Upcoming"
                            ? "bg-yellow-100 text-yellow-800"
                            : status === "Completed"
                            ? "bg-green-100 text-green-800"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {status}
                      </span>
                    </div>
                  </div>
                  <div className='space-y-1'>
                    <p className='text-sm font-medium'>Description</p>
                    <p className='text-sm text-muted-foreground'>
                      This is a(n) {assessment.type.toLowerCase()} for {assessment.course}. Students
                      will be evaluated on their knowledge of the course material.
                    </p>
                  </div>
                </div>
                <DialogFooter>
                  <DialogClose asChild>
                    <Button type='button' variant='outline'>
                      Close
                    </Button>
                  </DialogClose>
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
                <DropdownMenuItem className='cursor-pointer'>
                  <Calendar className='mr-2 h-4 w-4' />
                  Reschedule
                </DropdownMenuItem>
                <DropdownMenuItem className='cursor-pointer'>
                  <Edit className='mr-2 h-4 w-4' />
                  Edit Assessment
                </DropdownMenuItem>
                <DropdownMenuItem className='cursor-pointer'>
                  <Trash className='mr-2 h-4 w-4' />
                  Delete Assessment
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        );
      },
    },
  ];

  // Initialize the table
  const table = useReactTable({
    data: assessments,
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
    <div className='contaner px-2 py-8 mx-auto h-ull'>
      <div className='flex justify-between items-center mb-8'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Assessments</h1>
          <p className='text-muted-foreground mt-1'>
            Manage your institution&apos;s assessments and grading
          </p>
        </div>
        <AddAssessment />
      </div>

      {/* Filters */}
      <div className='flex flex-wrap items-center mb-6 gap-3'>
        <div className='relative flex-1 min-w-[200px] max-w-sm'>
          <Search className='absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground' />
          <Input
            placeholder='Search assessments...'
            className='pl-8'
            value={globalFilter.title || ""}
            onChange={(e) => {
              setGlobalFilter({ ...globalFilter, title: e.target.value });
              table.setPageIndex(0);
            }}
          />
        </div>

        <div className='flex flex-wrap items-center gap-2'>
          <Select
            onValueChange={(value) => {
              //   table.getColumn("type")?.setFilterValue(value === "all" ? undefined : [value]);
              setGlobalFilter({ ...globalFilter, type: value === "all" ? undefined : value });
            }}
          >
            <SelectTrigger className='w-[150px]'>
              <SelectValue placeholder='Filter by type' />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='all'>All Types</SelectItem>
              <SelectItem value='Assignment'>Assignment</SelectItem>
              <SelectItem value='Exam'>Exam</SelectItem>
              <SelectItem value='Quiz'>Quiz</SelectItem>
            </SelectContent>
          </Select>

          <Select
            onValueChange={(value) => {
              table.getColumn("status")?.setFilterValue(value === "all" ? undefined : [value]);
            }}
          >
            <SelectTrigger className='w-[150px]'>
              <SelectValue placeholder='Filter by status' />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='all'>All Statuses</SelectItem>
              <SelectItem value='Active'>Active</SelectItem>
              <SelectItem value='Upcoming'>Upcoming</SelectItem>
              <SelectItem value='Completed'>Completed</SelectItem>
            </SelectContent>
          </Select>

          <Select
            onValueChange={(value) => {
              if (value === "all") {
                table.resetSorting();
              } else if (value === "earliest") {
                table.setSorting([{ id: "due_date", desc: false }]);
              } else if (value === "latest") {
                table.setSorting([{ id: "due_date", desc: true }]);
              }
            }}
          >
            <SelectTrigger className='w-[150px]'>
              <SelectValue placeholder='Sort by date' />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='all'>Default</SelectItem>
              <SelectItem value='earliest'>Earliest Due</SelectItem>
              <SelectItem value='latest'>Latest Due</SelectItem>
            </SelectContent>
          </Select>
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
                  <Loader2 className='size-10 mx-auto animate-spin text-primary' />
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
                <TableCell colSpan={columns.length} className='h-24 text-center'>
                  No assessments found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className='flex items-center justify-between gap-2 py-4'>
        <div className='text-sm text-muted-foreground'>
          Showing {assessments.length > 0 ? 1 : 0} to {assessments.length} of{" "}
          {data?.pages[0]?.total_items || 0} assessments
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
            <div className='flex items-center justify-center gap-2'>
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
