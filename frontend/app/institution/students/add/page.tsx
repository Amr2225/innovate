"use client";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import React, { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { AxiosError } from "axios";
import { apiUserImport } from "@/lib/api";
import { useMutation } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import StatusDialog from "@/app/institution/students/_components/status-dialog";
import { SubmissionData } from "@/types/user.types";
import moment from "moment";
import { getSession } from "@/lib/session";

const formSchema = z.object({
  excelFile: z
    .instanceof(File, { message: "Excel file is required" })
    .refine((file) => file.size > 0, "Please select a file")
    .refine(
      (file) =>
        file.type === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
        file.type === "application/vnd.ms-excel" ||
        file.type === "text/csv",
      "Please upload an Excel file (.xlsx or .xls or .csv)"
    ),
});

interface UserResponse {
  first_name: string;
  middle_name: string;
  last_name: string;
  email: string;
  role: string;
  national_id: string;
  birth_date: string;
  age: number;
}

interface BulkInsertResponse {
  success: boolean;
  created_users: UserResponse[];
  errors: {
    row: UserResponse;
    errors: {
      [key: string]: string[];
    };
  }[];
}

const transformData = (data: BulkInsertResponse, institution: string): SubmissionData[] => {
  const transformedData: SubmissionData[] = [];

  data.errors.forEach((record) => {
    transformedData.push({
      name: record.row.first_name + " " + record.row.middle_name + " " + record.row.last_name,
      email: record.row.email ?? "-",
      role: record.row.role,
      institution: institution,
      national_id: record.row.national_id,
      birth_date: moment(record.row.birth_date).format("YYYY-MM-DD"),
      age: record.row.age,
      error: Object.values(record.errors)[0][0],
    });
  });

  data.created_users.forEach((record) => {
    transformedData.push({
      name: record.first_name + " " + record.middle_name + " " + record.last_name,
      email: record.email,
      role: record.role,
      institution: institution,
      national_id: record.national_id,
      birth_date: moment(record.birth_date).format("YYYY-MM-DD"),
      age: record.age,
    });
  });

  return transformedData;
};

const BulkInster = async (formData: FormData): Promise<SubmissionData[]> => {
  const res = await apiUserImport.post("/auth/institution/users/register/csv/", formData);
  const session = await getSession();
  if (!session) {
    throw new Error("Session not found");
  }
  return transformData(res.data, session.user.name);
};

export default function AddStudentPage() {
  const [open, setOpen] = useState(false);

  const {
    mutate: submitData,
    isPending,
    isSuccess,
    data,
  } = useMutation({
    mutationFn: (formData: FormData) => BulkInster(formData),
  });

  useEffect(() => {
    if (isSuccess) {
      setOpen(true);
    }
  }, [isSuccess]);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      excelFile: undefined,
    },
  });

  const handleAddStudent = async (data: z.infer<typeof formSchema>) => {
    const formData = new FormData();
    formData.append("file", data.excelFile);

    try {
      submitData(formData);
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) fileInput.value = "";
    } catch (error) {
      if (error instanceof AxiosError) {
        console.log("Error uploading file:", error.response?.data);
      }
    }
  };

  return (
    <div>
      <h1>Student</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleAddStudent)} className='space-y-4'>
          <FormField
            control={form.control}
            name='excelFile'
            render={({ field: { onChange, ...field } }) => (
              <FormItem>
                <FormLabel>Excel File</FormLabel>
                <FormControl>
                  <Input
                    type='file'
                    accept='.xlsx,.xls,.csv'
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      onChange(file);
                    }}
                    {...{ ...field, value: undefined }}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <Button type='submit' disabled={isPending}>
            {isPending ? <Loader2 className='w-4 h-4 animate-spin' /> : "Add Student"}
          </Button>

          <Button variant='secondary' type='button' onClick={() => setOpen(true)} className='ml-8'>
            Show Status
          </Button>
        </form>
      </Form>

      <StatusDialog open={open} onOpenChange={setOpen} data={data ?? []} />
    </div>
  );
}
