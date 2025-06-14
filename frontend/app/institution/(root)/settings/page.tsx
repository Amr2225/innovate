"use client";

import { useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Switch } from "@/components/ui/switch";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { CalendarIcon } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { useForm } from "react-hook-form";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { getInstitutionPolicy, updateInstitutionPolicy } from "@/apiService/institutionPolicy";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { InstitutionPolicy } from "@/types/institution.type";

export default function InstitutionPolicyPage() {
  const queryClient = useQueryClient();

  const { data: policy, isLoading: isPolicyLoading } = useQuery({
    queryKey: ["institution-policy"],
    queryFn: () => getInstitutionPolicy(),
  });

  const { mutate: updatePolicy, isPending: isUpdating } = useMutation({
    mutationFn: (policy: InstitutionPolicy) => updateInstitutionPolicy(policy),
    onSuccess: () => {
      toast.success("Policy updated successfully");
      queryClient.invalidateQueries({ queryKey: ["institution-policy"] });
    },
    onError: () => {
      toast.error("Failed to update policy");
    },
  });

  const form = useForm<InstitutionPolicy>({
    defaultValues: {
      min_passing_percentage: 0,
      max_allowed_failures: 0,
      min_gpa_required: 0,
      min_attendance_percent: 0,
      max_allowed_courses_per_semester: 0,
      year_registration_open: true,
      summer_registration_open: false,
      promotion_time: undefined,
    },
  });

  useEffect(() => {
    if (policy && !isPolicyLoading) {
      form.reset({
        min_passing_percentage: policy.min_passing_percentage || 0,
        max_allowed_failures: policy.max_allowed_failures || 0,
        min_gpa_required: policy.min_gpa_required || 0,
        min_attendance_percent: policy.min_attendance_percent || 0,
        max_allowed_courses_per_semester: policy.max_allowed_courses_per_semester || 0,
        year_registration_open: policy.year_registration_open || false,
        summer_registration_open: policy.summer_registration_open ?? false,
        promotion_time: policy.promotion_time || undefined,
      });
    }
  }, [form, policy, isPolicyLoading]);

  return (
    <div className='container max-w-4xl py-10'>
      <div className='space-y-6'>
        {/* Institution Access Code Section */}
        <Card>
          <CardHeader>
            <CardTitle>Institution Access Code</CardTitle>
          </CardHeader>
          <CardContent>
            <div className='flex items-center justify-between p-4 bg-muted rounded-lg'>
              <div className='space-y-1'>
                <p className='text-sm text-muted-foreground'>Your institution access code</p>
                <p className='text-2xl font-mono font-bold'>{policy?.access_code}</p>
              </div>
              <Button
                variant='outline'
                onClick={() => {
                  navigator.clipboard.writeText(policy?.access_code || "");
                  toast.success("Access code copied to clipboard");
                }}
              >
                Copy Code
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Policy Settings Form */}
        <Form {...form}>
          <form onSubmit={form.handleSubmit((data) => updatePolicy(data))}>
            <Card>
              <CardHeader>
                <CardTitle>Academic Policy Settings</CardTitle>
              </CardHeader>
              <CardContent className='space-y-6'>
                <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
                  {/* Minimum Passing Percentage */}
                  <FormField
                    control={form.control}
                    name='min_passing_percentage'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Minimum Passing Percentage</FormLabel>
                        <FormControl>
                          <Input
                            type='number'
                            min='0'
                            max='100'
                            {...field}
                            value={field.value || ""}
                            onChange={(e) => field.onChange(Number(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* Maximum Allowed Failures */}
                  <FormField
                    control={form.control}
                    name='max_allowed_failures'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Maximum Allowed Failures</FormLabel>
                        <FormControl>
                          <Input
                            type='number'
                            min='0'
                            {...field}
                            value={field.value || ""}
                            onChange={(e) => field.onChange(Number(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* Minimum GPA Required */}
                  <FormField
                    control={form.control}
                    name='min_gpa_required'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Minimum GPA Required</FormLabel>
                        <FormControl>
                          <Input
                            type='number'
                            step='0.1'
                            min='0'
                            max='4'
                            {...field}
                            value={field.value || ""}
                            onChange={(e) => field.onChange(Number(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* Minimum Attendance Percent */}
                  <FormField
                    control={form.control}
                    name='min_attendance_percent'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Minimum Attendance Percent</FormLabel>
                        <FormControl>
                          <Input
                            type='number'
                            min='0'
                            max='100'
                            {...field}
                            value={field.value || ""}
                            onChange={(e) => field.onChange(Number(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* Maximum Allowed Courses */}
                  <FormField
                    control={form.control}
                    name='max_allowed_courses_per_semester'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Maximum Courses per Semester</FormLabel>
                        <FormControl>
                          <Input
                            type='number'
                            min='1'
                            {...field}
                            value={field.value || ""}
                            onChange={(e) => field.onChange(Number(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* Promotion Time */}
                  <FormField
                    control={form.control}
                    name='promotion_time'
                    render={({ field }) => (
                      <FormItem className='flex flex-col mt-2.5'>
                        <FormLabel>Promotion Time</FormLabel>
                        <Popover>
                          <PopoverTrigger asChild>
                            <FormControl>
                              <Button
                                variant='outline'
                                className={cn(
                                  "w-full pl-3 text-left font-normal",
                                  !field.value && "text-muted-foreground"
                                )}
                              >
                                {field.value ? (
                                  format(field.value, "PPP")
                                ) : (
                                  <span>Pick a date</span>
                                )}
                                <CalendarIcon className='ml-auto h-4 w-4 opacity-50' />
                              </Button>
                            </FormControl>
                          </PopoverTrigger>
                          <PopoverContent className='w-auto p-0' align='start'>
                            <Calendar
                              mode='single'
                              selected={field.value || undefined}
                              onSelect={field.onChange}
                              disabled={(date) => date < new Date("1900-01-01")}
                              initialFocus
                            />
                          </PopoverContent>
                        </Popover>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                {/* Registration Toggles */}
                <div className='space-y-4 pt-4'>
                  <FormField
                    control={form.control}
                    name='year_registration_open'
                    render={({ field }) => (
                      <FormItem className='flex items-center justify-between rounded-lg border p-4'>
                        <div className='space-y-0.5'>
                          <FormLabel>Year Registration</FormLabel>
                          <p className='text-sm text-muted-foreground'>
                            Allow students to register for the academic year
                          </p>
                        </div>
                        <FormControl>
                          <Switch checked={field.value || false} onCheckedChange={field.onChange} />
                        </FormControl>
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name='summer_registration_open'
                    render={({ field }) => (
                      <FormItem className='flex items-center justify-between rounded-lg border p-4'>
                        <div className='space-y-0.5'>
                          <FormLabel>Summer Registration</FormLabel>
                          <p className='text-sm text-muted-foreground'>
                            Allow students to register for summer courses
                          </p>
                        </div>
                        <FormControl>
                          <Switch checked={field.value || false} onCheckedChange={field.onChange} />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                </div>

                <Button type='submit' className='w-full' disabled={isUpdating}>
                  {isUpdating ? "Saving..." : "Save Changes"}
                </Button>
              </CardContent>
            </Card>
          </form>
        </Form>
      </div>
    </div>
  );
}
