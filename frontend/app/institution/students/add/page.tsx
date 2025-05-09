"use client";
import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { useMutation } from "@tanstack/react-query";

// Components
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import StatusDialog from "@/app/institution/students/_components/status-dialog";
import { Input } from "@/components/ui/input";

import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";

// API
import { AxiosError } from "axios";

// Schema
import { BulkUserSchema, BulkUserSchemaType } from "@/schema/bulkUserSchema";
import { toast } from "sonner";

// Services
import { institutionService } from "@/apiService/services";

export default function AddStudentPage() {
  const [open, setOpen] = useState(false);

  const {
    mutate: submitData,
    isPending,
    data,
  } = useMutation({
    mutationFn: (formData: FormData) => institutionService.bulkUserInsert(formData),
    onError: () => {
      toast.error("Failed to add students");
    },
    onSuccess: () => {
      setOpen(true);
    },
  });

  const form = useForm<BulkUserSchemaType>({
    resolver: zodResolver(BulkUserSchema),
    defaultValues: {
      excelFile: undefined,
    },
  });

  const handleAddStudent = async (data: BulkUserSchemaType) => {
    const formData = new FormData();
    formData.append("file", data.excelFile);

    try {
      submitData(formData);
      // const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      // if (fileInput) fileInput.value = "";
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
