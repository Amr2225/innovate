"use client";

import React, { useState } from "react";
import {
  Table,
  TableHeader,
  TableHead,
  TableRow,
  TableBody,
  TableCell,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useInfiniteQuery } from "@tanstack/react-query";
import { useDebounce } from "use-debounce";
import { InstitutionMembersType } from "@/types/user.types";
import { Search, ArrowUpDown, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { institutionService } from "@/apiService/services";
import moment from "moment";

interface GlobalFilter {
  first_name?: string;
  last_name?: string;
  email?: string;
}

export default function TeacherStudentsPage() {
  // Table state
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [globalFilter, setGlobalFilter] = useState<GlobalFilter>({
    first_name: undefined,
    last_name: undefined,
    email: undefined,
  });
  const [debouncedFilter] = useDebounce(globalFilter, 500);

  // Fetch data from API
  const {
    data,
    isError,
    hasNextPage,
    fetchNextPage,
    hasPreviousPage,
    fetchPreviousPage,
    isFetchingNextPage,
    isFetchingPreviousPage,
  } = useInfiniteQuery({
    queryKey: ["teacher-students", debouncedFilter, currentPage],
    queryFn: ({ pageParam }) =>
      institutionService.getMembers({
        pageParam,
        pageSize: 10,
        first_name: debouncedFilter.first_name,
        last_name: debouncedFilter.last_name,
        email: debouncedFilter.email,
        role: "Student", // Only fetch students
      }),
    initialPageParam: currentPage,
    maxPages: 1,
    getNextPageParam: (lastPage) => lastPage.next,
    getPreviousPageParam: (firstPage) => firstPage.previous,
  });

  // Extract students from paginated response
  const students = data?.pages.flatMap((page) => page.data) || [];

  // Column definitions
  const columns: ColumnDef<InstitutionMembersType>[] = [
    {
      accessorKey: "national_id",
      header: ({ column }) => (
        <div className='flex items-center space-x-1'>
          <span>National ID</span>
          <Button
            variant='ghost'
            className='p-0 h-6 w-6'
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            <ArrowUpDown className='h-3 w-3' />
          </Button>
        </div>
      ),
      cell: ({ row }) => <div>{row.getValue("national_id")}</div>,
    },
    {
      accessorKey: "first_name",
      header: ({ column }) => (
        <div className='flex items-center space-x-1'>
          <span>First Name</span>
          <Button
            variant='ghost'
            className='p-0 h-6 w-6'
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            <ArrowUpDown className='h-3 w-3' />
          </Button>
        </div>
      ),
      cell: ({ row }) => <div>{row.getValue("first_name")}</div>,
    },
    {
      accessorKey: "middle_name",
      header: "Middle Name",
      cell: ({ row }) => <div>{row.getValue("middle_name") || "-"}</div>,
    },
    {
      accessorKey: "last_name",
      header: ({ column }) => (
        <div className='flex items-center space-x-1'>
          <span>Last Name</span>
          <Button
            variant='ghost'
            className='p-0 h-6 w-6'
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            <ArrowUpDown className='h-3 w-3' />
          </Button>
        </div>
      ),
      cell: ({ row }) => <div>{row.getValue("last_name")}</div>,
    },
    {
      accessorKey: "email",
      header: ({ column }) => (
        <div className='flex items-center space-x-1'>
          <span>Email</span>
          <Button
            variant='ghost'
            className='p-0 h-6 w-6'
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            <ArrowUpDown className='h-3 w-3' />
          </Button>
        </div>
      ),
      cell: ({ row }) => <div>{row.getValue("email")}</div>,
    },
    {
      accessorKey: "birth_date",
      header: "Birth Date",
      cell: ({ row }) => (
        <div>
          {row.getValue("birth_date")
            ? moment(row.getValue("birth_date")).format("MMM DD, YYYY")
            : "-"}
        </div>
      ),
    },
    {
      accessorKey: "age",
      header: ({ column }) => (
        <div className='flex items-center space-x-1'>
          <span>Age</span>
          <Button
            variant='ghost'
            className='p-0 h-6 w-6'
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            <ArrowUpDown className='h-3 w-3' />
          </Button>
        </div>
      ),
      cell: ({ row }) => <div className='text-center'>{row.getValue("age")}</div>,
    },
    {
      accessorKey: "date_joined",
      header: "Date Joined",
      cell: ({ row }) => (
        <div>
          {row.getValue("date_joined")
            ? moment(row.getValue("date_joined")).format("MMM DD, YYYY")
            : "-"}
        </div>
      ),
      sortingFn: "datetime",
    },
  ];

  // Initialize the table
  const table = useReactTable({
    data: students,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    state: {
      sorting,
      columnFilters,
    },
  });

  if (isError) return <div>Error loading student data</div>;

  return (
    <div className='container py-8 mx-auto'>
      <div className='flex justify-between items-center mb-8'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Students</h1>
          <p className='text-muted-foreground mt-1'>View your students information</p>
        </div>
      </div>

      {/* Filters */}
      <div className='flex flex-wrap items-center mb-6 gap-3'>
        <div className='relative flex-1 min-w-[200px] max-w-sm'>
          <Search className='absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground' />
          <Input
            placeholder='Search students...'
            className='pl-8'
            value={globalFilter.first_name || ""}
            onChange={(e) => setGlobalFilter({ ...globalFilter, first_name: e.target.value })}
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
            {students.length ? (
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
                  No students found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination controls */}
      <div className='flex items-center justify-between space-x-2 py-4'>
        <div className='text-sm text-muted-foreground'>
          Showing {students.length > 0 ? 1 : 0} to {students.length} of{" "}
          {data?.pages[0]?.total_items || 0} students
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
                let pageNumber;
                if (data.pages[0].total_pages <= 5) {
                  pageNumber = i + 1;
                } else if (currentPage <= 3) {
                  pageNumber = i + 1;
                } else if (currentPage >= data.pages[0].total_pages - 2) {
                  pageNumber = data.pages[0].total_pages - 4 + i;
                } else {
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
