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
import Loader from "@/components/Loader";
import { Loader2, Info } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

function InfoDisplay({ message }: { message: string }) {
  return (
    <Card className='border-blue-200 bg-blue-50/50 mt-12'>
      <CardHeader>
        <div className='flex items-center gap-2 text-blue-600'>
          <Info className='h-5 w-5' />
          <CardTitle>Course Registration</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className='space-y-4'>
          <p className='text-muted-foreground'>{message}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function EnrollSection() {
  const { availableCourses, isLoading, error } = useEnrollment();

  if (isLoading) return <Loader />;

  if (error && !availableCourses)
    return (
      <InfoDisplay
        message={error.message || "Registration is not open at this time. Please check back later."}
      />
    );

  console.log(availableCourses);

  return (
    <div>
      <h1 className='text-xl font-bold mt-3'>Available Courses</h1>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Course Name</TableHead>
            <TableHead>Course Description</TableHead>
            <TableHead>Course Teacher</TableHead>
            {availableCourses?.[0]?.credit_hours && <TableHead>Credit Hours</TableHead>}
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {availableCourses?.map((course) => (
            <TableRow key={course.id}>
              <TableCell>{course.name}</TableCell>
              <TableCell>{course.description}</TableCell>
              <TableCell>
                <div className='space-y-2'>
                  {course.instructors && course.instructors.length > 0 ? (
                    course.instructors.map((instructor) => (
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
                        <p className='text-sm font-medium text-neutral-700'>
                          {instructor.full_name}
                        </p>
                      </div>
                    ))
                  ) : (
                    <p className='text-sm font-medium text-neutral-700'>No instructor assigned</p>
                  )}
                </div>
              </TableCell>
              {course.credit_hours && <TableCell>{course.credit_hours}</TableCell>}
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
