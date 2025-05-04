"use client";
import React from "react";
import { useForm } from "react-hook-form";

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function BasInfoForm() {
  const form = useForm({
    defaultValues: {
      title: "",
      subtitle: "",
      course: "",
      course_category: "",
      course_topic: "",
      course_level: "",
    },
  });

  const handleNext = (data: unknown) => {
    console.log(data);
  };

  return (
    <div className='mt-5'>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleNext)} className='space-y-4'>
          <FormField
            control={form.control}
            name='title'
            render={({ field }) => (
              <FormItem>
                <FormLabel>Title</FormLabel>
                <FormControl>
                  <Input placeholder='Title' {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name='subtitle'
            render={({ field }) => (
              <FormItem>
                <FormLabel>Subtitle</FormLabel>
                <FormControl>
                  <Input placeholder='Subtitle' {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name='course'
            render={({ field }) => (
              <FormItem>
                <FormLabel>Course</FormLabel>
                <FormControl>
                  <Input placeholder='Course' {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name='course_category'
            render={({ field }) => (
              <FormItem>
                <FormLabel>Course Category</FormLabel>
                <FormControl>
                  <Input placeholder='Course Category' {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name='course_topic'
            render={({ field }) => (
              <FormItem>
                <FormLabel>Course Topic</FormLabel>
                <Input placeholder='Course Topic' {...field} />
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name='course_level'
            render={({ field }) => (
              <FormItem>
                <FormLabel>Course Level</FormLabel>
                <FormControl>
                  <Input
                    type='file'
                    className='file:bg-muted items-center flex justify-center file:h-full px-0 file:p-2 p-0'
                    placeholder='Course Level'
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className='flex justify-between items-center mt-10 '>
            <Button type='button' variant={"secondary"}>
              Cancel
            </Button>
            <Button type='submit'>Save & Next</Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
