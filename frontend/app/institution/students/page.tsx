"use client";
import { institutionService } from "@/apiService/services";
import { DataTableSkeleton } from "@/components/helpers/data-table-skeleton";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableHeader,
  TableHead,
  TableRow,
  TableBody,
  TableCell,
  TableCaption,
} from "@/components/ui/table";
import { useInfiniteQuery } from "@tanstack/react-query";
import moment from "moment";
import React from "react";

export default function StudentsPage() {
  const {
    data,
    isLoading,
    isError,
    hasNextPage,
    fetchNextPage,
    hasPreviousPage,
    fetchPreviousPage,
  } = useInfiniteQuery({
    queryKey: ["institution-users"],
    queryFn: ({ pageParam }) => institutionService.getMembers(pageParam, 2),
    initialPageParam: 1,
    maxPages: 1,
    getNextPageParam: (lastPage) => lastPage.next,
    getPreviousPageParam: (firstPage) => firstPage.previous,
    select(data) {
      return data.pages.flatMap((page) => page.data);
    },
  });

  if (isLoading)
    return (
      <div className='px-4 py-3'>
        <h1 className='text-2xl font-bold'>Users Data</h1>
        <DataTableSkeleton
          columnCount={12}
          rowCount={5}
          withPagination={false}
          withViewOptions={false}
        />
      </div>
    );
  if (isError || !data) return <div>Error</div>;

  console.log(data, hasNextPage);

  // TODO: implement pagination and filtering
  return (
    <div className='px-4 py-3'>
      <h1 className='text-2xl font-bold mb-4'>Users Data</h1>

      <Table>
        <TableCaption>Users Data</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>National ID</TableHead>
            <TableHead>First Name</TableHead>
            <TableHead>Middle Name</TableHead>
            <TableHead>Last Name</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>Birth Date</TableHead>
            <TableHead>Age</TableHead>
            <TableHead>Role</TableHead>
            <TableHead>Institution</TableHead>
            <TableHead>Date Joined</TableHead>
            <TableHead>Is Email Verified</TableHead>
            <TableHead>Is Account Active</TableHead>
          </TableRow>
        </TableHeader>

        <TableBody>
          {data.map((user) => (
            <TableRow key={user.id}>
              <TableCell>{user.national_id}</TableCell>
              <TableCell>{user.first_name}</TableCell>
              <TableCell>{user.middle_name}</TableCell>
              <TableCell>{user.last_name}</TableCell>
              <TableCell>{user.email}</TableCell>
              <TableCell>{moment(user.birth_date).format("DD/MM/YYYY")}</TableCell>
              <TableCell>{user.age}</TableCell>
              <TableCell>{user.role}</TableCell>
              <TableCell>{user.institution}</TableCell>
              <TableCell>{moment(user.date_joined).format("DD/MM/YYYY")}</TableCell>
              <TableCell>{user.is_email_verified ? "Yes" : "No"}</TableCell>
              <TableCell>{user.is_active ? "Yes" : "No"}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <div className='flex justify-between items-center gap-2'>
        <Button disabled={!hasPreviousPage} onClick={() => fetchPreviousPage()}>
          Previous
        </Button>
        <Button disabled={!hasNextPage} onClick={() => fetchNextPage()}>
          Next
        </Button>
      </div>
    </div>
  );
}
