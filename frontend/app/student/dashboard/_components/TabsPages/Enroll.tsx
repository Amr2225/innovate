"use client";
import React, { useState } from "react";
import {
  TableHeader,
  TableHead,
  Table,
  TableCell,
  TableRow,
  TableBody,
} from "@/components/ui/table";
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
import { Button } from "@/components/ui/button";
import { useEnrollment } from "@/queryHooks/useEnrollment";
import Loader from "../Loader";
import { Loader2 } from "lucide-react";

export default function EnrollSection() {
  const { availableCourses, isLoading, error } = useEnrollment();

  if (isLoading) return <Loader />;

  if (error) return null;

  return (
    <div>
      <h1 className='text-xl font-bold mt-3'>Available Courses</h1>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Course Name</TableHead>
            <TableHead>Course Description</TableHead>
            <TableHead>Course Teacher</TableHead>
            {/* TODO: think of how to differentiate between college and school */}
            <TableHead>Credit Hours</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {availableCourses?.data.map((course) => (
            <TableRow key={course.id}>
              <TableCell>{course.name}</TableCell>
              <TableCell>{course.description}</TableCell>
              <TableCell>{course.instructors[0]?.full_name || "-"}</TableCell>
              <TableCell>{course.credit_hours}</TableCell>
              <TableCell>
                <EnrollButton courseId={course.id} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

const EnrollButton = ({ courseId }: { courseId: string }) => {
  const [open, setOpen] = useState(false);
  const { enroll, isEnrolling } = useEnrollment();
  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogTrigger asChild>
        <Button disabled={isEnrolling} className='w-[70%]'>
          {isEnrolling ? <Loader2 className='size-4 animate-spin' /> : "Enroll"}
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This will enroll you in this course. You will be able to access course materials and
            participate in class activities once enrolled.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction disabled={isEnrolling} onClick={() => enroll(courseId)}>
            Continue
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};
