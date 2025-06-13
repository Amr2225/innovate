"use client";
import React, { useState } from "react";

import { DialogFooter } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { Plus, Upload } from "lucide-react";
import { toast } from "sonner";
import { BirthDatePicker } from "@/components/date-picker";
import CustomDialog from "@/components/CustomDialog";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  InstitutionRegisterStudentSchema,
  InstitutionRegisterStudentSchemaType,
} from "@/schema/institutionRegisterSchema";
import {
  FormControl,
  FormField,
  FormItem,
  FormMessage,
  Form,
  FormLabel,
} from "@/components/ui/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { institutionService } from "@/apiService/services";
import { BulkUserSchema, BulkUserSchemaType } from "@/schema/bulkUserSchema";
import StatusDialog from "./status-dialog";

export default function AddStudentDialog() {
  const [activeTab, setActiveTab] = useState("form");
  const [isAddUserOpen, setIsAddUserOpen] = useState(false);
  const [studentDialogOpen, setStudentDialogOpen] = useState(false);
  const queryClient = useQueryClient();

  const form = useForm<InstitutionRegisterStudentSchemaType>({
    resolver: zodResolver(InstitutionRegisterStudentSchema),
    defaultValues: {
      first_name: "",
      middle_name: "",
      last_name: "",
      email: "",
      role: "Student",
      national_id: "",
      birth_date: null,
    },
  });

  const csvForm = useForm<BulkUserSchemaType>({
    resolver: zodResolver(BulkUserSchema),
    defaultValues: {
      excelFile: undefined,
    },
  });

  const { mutate: registerSingleUser } = useMutation({
    mutationFn: (data: InstitutionRegisterStudentSchemaType) =>
      institutionService.registerSingleUser(data),
    onSuccess: () => {
      toast.success("User registered successfully");
      queryClient.invalidateQueries({ queryKey: ["institution-users"] });
      setIsAddUserOpen(false);
      form.reset();
    },
    onError: () => {
      toast.error("Failed to register user");
    },
  });

  // CSV
  const { mutate: bulkUserInsert, data: bulkUserData } = useMutation({
    mutationFn: (formData: FormData) => institutionService.bulkUserInsert(formData),
    onSuccess: () => {
      toast.success("Users registered successfully");
      queryClient.invalidateQueries({ queryKey: ["institution-users"] });
      setStudentDialogOpen(true);
      csvForm.reset();
    },
    onError: () => {
      toast.error("Failed to add students");
    },
  });

  const handleSubmit = (data: InstitutionRegisterStudentSchemaType) => {
    registerSingleUser(data);
  };

  // Handle CSV upload submission
  const handleAddStudentCSV = async (data: BulkUserSchemaType) => {
    const formData = new FormData();
    formData.append("file", data.excelFile);

    bulkUserInsert(formData);
  };

  return (
    <CustomDialog
      title='Add New User'
      description='Add a new user to your institution or upload a CSV file with multiple users.'
      open={isAddUserOpen}
      setOpen={setIsAddUserOpen}
      trigger={
        <Button className='gap-1'>
          <Plus size={16} />
          Add User
        </Button>
      }
    >
      <Tabs value={activeTab} onValueChange={setActiveTab} className='mt-4'>
        <TabsList className='grid w-full grid-cols-2'>
          <TabsTrigger value='form'>Manual Entry</TabsTrigger>
          <TabsTrigger value='csv'>CSV Upload</TabsTrigger>
        </TabsList>

        <TabsContent value='form' className='pt-4'>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(handleSubmit)}>
              <div className='grid grid-cols-2 gap-4'>
                <FormField
                  control={form.control}
                  name='first_name'
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input placeholder='First Name' {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name='middle_name'
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input placeholder='Middle Name' {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name='last_name'
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input placeholder='Last Name' {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name='email'
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input placeholder='Email' {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name='national_id'
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input placeholder='National ID' {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name='birth_date'
                  render={({ field }) => (
                    <BirthDatePicker date={field.value ?? undefined} setDate={field.onChange} />
                  )}
                />

                <FormField
                  control={form.control}
                  name='role'
                  render={({ field }) => (
                    <FormItem className='col-span-2'>
                      <FormControl>
                        <Select value={field.value} onValueChange={field.onChange}>
                          <SelectTrigger>
                            <SelectValue placeholder='Select a role' />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value='Student'>Student</SelectItem>
                            <SelectItem value='Teacher'>Teacher</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className='pt-4 text-xs text-muted-foreground'>
                Fields marked with * are required
              </div>

              <DialogFooter>
                <Button type='submit'>Add User</Button>
              </DialogFooter>
            </form>
          </Form>
        </TabsContent>

        <TabsContent value='csv' className='pt-4'>
          <Form {...csvForm}>
            <form onSubmit={csvForm.handleSubmit(handleAddStudentCSV)} className='space-y-4'>
              <div className='grid gap-4'>
                <FormField
                  control={csvForm.control}
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
              </div>

              <div className='space-y-2'>
                <Label>CSV Format Requirements</Label>
                <div className='text-sm text-muted-foreground border rounded-md p-3'>
                  <p className='mb-2'>Your CSV file should include the following columns:</p>
                  <ul className='list-disc pl-5 space-y-1'>
                    <li>first_name (required)</li>
                    <li>last_name (required)</li>
                    <li>middle_name (optional)</li>
                    <li>email (required)</li>
                    <li>national_id (required)</li>
                    <li>birth_date (format: YYYY-MM-DD)</li>
                    <li>role (Student, Teacher, or Administrator)</li>
                  </ul>
                </div>
              </div>

              <div className='flex items-center gap-2'>
                <Button variant='outline' type='button'>
                  <a href='/templates/users_template.csv' download>
                    Download Template
                  </a>
                </Button>
              </div>

              <DialogFooter>
                <Button type='submit' className='gap-1'>
                  <Upload size={16} />
                  Upload CSV
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </TabsContent>
      </Tabs>

      <StatusDialog
        open={studentDialogOpen}
        onOpenChange={setStudentDialogOpen}
        data={bulkUserData ?? []}
      />
    </CustomDialog>
  );
}
