"use client";
import { institutionService } from "@/apiService/services";
// import { DataTableSkeleton } from "@/components/helpers/data-table-skeleton";
import { Button } from "@/components/ui/button";
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
import EditableCell from "./_components/editableCell";

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
import { useInfiniteQuery, useMutation } from "@tanstack/react-query";
import { useDebounce } from "use-debounce";
import { InstitutionMembersType } from "@/types/user.types";
import React, { useState, useMemo } from "react";
import { Search, ArrowUpDown, ChevronLeft, ChevronRight, Trash2, Loader2 } from "lucide-react";
import { toast } from "sonner";
import AddStudentDialog from "./_components/addStudentDialog";
// import { updateUser } from "@/apiService/institutionService";
import { useAuth } from "@/hooks/useAuth";

interface GlobalFilter {
  first_name?: string;
  last_name?: string;
  email?: string;
}

const uniqueRoles = ["Student", "Teacher"];
export default function StudentsPage() {
  // Table state
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [globalFilter, setGlobalFilter] = useState<GlobalFilter>({
    first_name: undefined,
    last_name: undefined,
    email: undefined,
  });
  const [deletingUserId, setDeletingUserId] = useState<string | null>(null);
  const [debouncedFilter] = useDebounce(globalFilter, 500);
  // const queryClient = useQueryClient();
  const { updateUser } = useAuth();

  // Fetch data from API
  // TODO: fix pagination
  const {
    data,
    // isLoading,
    isError,
    hasNextPage,
    fetchNextPage,
    hasPreviousPage,
    fetchPreviousPage,
    isFetchingNextPage,
    isFetchingPreviousPage,
    refetch,
  } = useInfiniteQuery({
    queryKey: ["institution-users", debouncedFilter, currentPage],
    queryFn: ({ pageParam }) =>
      institutionService.getMembers({
        pageParam,
        pageSize: 10,
        first_name: debouncedFilter.first_name,
        last_name: debouncedFilter.last_name,
        email: debouncedFilter.email,
      }),
    initialPageParam: currentPage,
    getNextPageParam: (lastPage) => lastPage.next,
    getPreviousPageParam: (firstPage) => firstPage.previous,
  });

  const { mutate: updateUserMutation } = useMutation({
    mutationFn: ({
      userId,
      data,
    }: {
      userId: string;
      data: Record<string, string | number | boolean | Date>;
    }) => institutionService.updateUser({ userId, data }),
  });

  const { mutate: deleteUserMutation } = useMutation({
    mutationFn: ({ userId }: { userId: string }) => institutionService.deleteUser({ userId }),
    onMutate: (data) => {
      setDeletingUserId(data.userId);
    },
    onSuccess: () => {
      toast.success("User deleted successfully");
      updateUser();
      refetch();
    },
    onError: () => {
      toast.error("Failed to delete user");
    },
    onSettled: () => {
      setDeletingUserId(null);
    },
  });
  // Extract users from paginated response
  const users = useMemo(() => data?.pages.flatMap((page) => page.data) || [], [data?.pages]);

  // Handle field update
  const handleUpdateField = async (
    userId: string,
    field: string,
    newValue: string | number | boolean | Date
  ) => {
    updateUserMutation(
      { userId, data: { [field]: newValue } },
      {
        onSuccess: () => {
          toast.success(`Updated User Successfully`);
          refetch();
        },
        onError: () => {
          toast.error(`Failed to update User`);
        },
      }
    );
  };

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
      cell: ({ row }) => (
        <EditableCell
          userId={row.original.id}
          value={row.getValue("national_id")}
          field='national_id'
          onSave={handleUpdateField}
        />
      ),
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
      cell: ({ row }) => (
        <EditableCell
          userId={row.original.id}
          value={row.getValue("first_name")}
          field='first_name'
          onSave={handleUpdateField}
        />
      ),
    },
    {
      accessorKey: "middle_name",
      header: "Middle Name",
      cell: ({ row }) => (
        <EditableCell
          userId={row.original.id}
          value={row.getValue("middle_name") || "-"}
          field='middle_name'
          onSave={handleUpdateField}
        />
      ),
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
      cell: ({ row }) => (
        <EditableCell
          userId={row.original.id}
          value={row.getValue("last_name")}
          field='last_name'
          onSave={handleUpdateField}
        />
      ),
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
      cell: ({ row }) => (
        <EditableCell
          userId={row.original.id}
          value={row.getValue("email")}
          field='email'
          onSave={handleUpdateField}
        />
      ),
    },
    {
      accessorKey: "birth_date",
      header: "Birth Date",
      cell: ({ row }) => (
        <EditableCell
          userId={row.original.id}
          value={row.getValue("birth_date") ?? "-"}
          field='birth_date'
          onSave={handleUpdateField}
        />
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
      cell: ({ row }) => (
        <div className='text-center'>
          <EditableCell
            userId={row.original.id}
            value={row.getValue("age")}
            field='age'
            onSave={handleUpdateField}
          />
        </div>
      ),
    },
    {
      accessorKey: "role",
      header: "Role",
      cell: ({ row }) => (
        <EditableCell
          userId={row.original.id}
          value={row.getValue("role")}
          field='role'
          onSave={handleUpdateField}
        />
      ),
      filterFn: (row, id, value) => {
        return value.includes(row.getValue(id));
      },
    },
    {
      accessorKey: "date_joined",
      header: "Date Joined",
      cell: ({ row }) => (
        <EditableCell
          userId={row.original.id}
          value={row.getValue("date_joined") ?? "-"}
          field='date_joined'
          onSave={handleUpdateField}
          isEditable={false}
        />
      ),
      sortingFn: "datetime",
    },
    {
      accessorKey: "is_email_verified",
      header: "Email Verified",
      cell: ({ row }) => (
        <EditableCell
          userId={row.original.id}
          value={row.getValue("is_email_verified")}
          field='is_email_verified'
          onSave={handleUpdateField}
        />
      ),
    },
    {
      accessorKey: "is_active",
      header: "Account Active",
      cell: ({ row }) => (
        <EditableCell
          userId={row.original.id}
          value={row.getValue("is_active")}
          field='is_active'
          onSave={handleUpdateField}
        />
      ),
    },
    {
      accessorKey: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button variant='destructive' size='sm' disabled={deletingUserId === row.original.id}>
              {deletingUserId === row.original.id ? (
                <Loader2 className='size-2.5 animate-spin' />
              ) : (
                <Trash2 className='size-2.5' />
              )}
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Are you sure?</AlertDialogTitle>
              <AlertDialogDescription>
                This action cannot be undone. This will permanently delete the student&apos;s
                account.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                disabled={deletingUserId === row.original.id}
                onClick={() => deleteUserMutation({ userId: row.original.id })}
              >
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      ),
    },
  ];

  // Initialize the table
  const table = useReactTable({
    data: users,
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

  // Extract unique roles for filter dropdown

  if (isError) return <div>Error loading student data</div>;

  return (
    <div className='container py-8 mx-auto'>
      <div className='flex justify-between items-center mb-8'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Students</h1>
          <p className='text-muted-foreground mt-1'>
            Manage your institution&apos;s students and users
          </p>
        </div>

        <AddStudentDialog />
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

        <div className='flex flex-wrap items-center gap-2'>
          <Select
            onValueChange={(value) => {
              table.getColumn("role")?.setFilterValue(value === "all" ? undefined : [value]);
            }}
          >
            <SelectTrigger className='w-[150px]'>
              <SelectValue placeholder='Filter by role' />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='all'>All Roles</SelectItem>
              {uniqueRoles.map((role) => (
                <SelectItem key={role} value={role}>
                  {role}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* {isLoading ? (
        // <div className='container px-4 py-8 mx-auto'>
        //   <h1 className='text-3xl font-bold mb-4'>Students</h1>
        <DataTableSkeleton
          columnCount={12}
          rowCount={5}
          withPagination={false}
          withViewOptions={false}
        />
      ) : ( */}
      <div className='border rounded-lg overflow-hidden bg-card'>
        <div className='text-xs text-muted-foreground p-2 bg-muted/50'>
          Double-click on any field to edit its value
        </div>
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
            {users.length ? (
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
          Showing {users.length > 0 ? 1 : 0} to {users.length} of {users.length} students
        </div>
        <div className='flex items-center space-x-2'>
          <Button
            variant='outline'
            size='sm'
            onClick={() => {
              fetchPreviousPage();
              setCurrentPage((prev) => prev - 1);
            }}
            disabled={!hasPreviousPage || isFetchingPreviousPage}
          >
            <ChevronLeft className='h-4 w-4' />
            <span className='sr-only'>Previous Page</span>
          </Button>
          <div className='text-sm font-medium'>Page {currentPage}</div>
          <Button
            variant='outline'
            size='sm'
            onClick={() => {
              fetchNextPage();
              setCurrentPage((prev) => prev + 1);
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
