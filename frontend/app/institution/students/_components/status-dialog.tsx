import React from "react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  //   AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
// import { Button } from "@/components/ui/button";
import { Table, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { TableHeader } from "@/components/ui/table";
import { SubmissionData } from "@/types/user.types";
import { cn } from "@/lib/utils";

interface StatusDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  data: SubmissionData[];
}

export default function StatusDialog({ open, onOpenChange, data }: StatusDialogProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className='min-w-max'>
        <AlertDialogHeader>
          <AlertDialogTitle>Import Status</AlertDialogTitle>
          <AlertDialogDescription>
            The following are the data of the imported students, wheather they were created or not.
          </AlertDialogDescription>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>National ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Birth Date</TableHead>
                <TableHead>Age</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Institution</TableHead>
                <TableHead>Error</TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {data.map((item) => (
                <TableRow key={item.national_id}>
                  <TableCell
                    className={cn(item.error && "!text-destructive", "text-green-600", "font-bold")}
                  >
                    {item.national_id}
                  </TableCell>
                  <TableCell>{item.name}</TableCell>
                  <TableCell>{item.email || "-"}</TableCell>
                  <TableCell>{item.birth_date}</TableCell>
                  <TableCell>{item.age}</TableCell>
                  <TableCell>{item.role}</TableCell>
                  <TableCell>{item.institution}</TableCell>
                  <TableCell>{item.error}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Close</AlertDialogCancel>
          <AlertDialogAction>Continue</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
