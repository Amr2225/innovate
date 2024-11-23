"use client";
import React from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
  FormDescription,
  FormLabel,
} from "@/components/ui/form";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import Link from "next/link";

import { useForm } from "react-hook-form";
import { accessLoginSchema, AccessLoginSchemaType } from "@/schema/accessLoginSchema";
import { zodResolver } from "@hookform/resolvers/zod";

export default function AccessLogin() {
  const form = useForm<AccessLoginSchemaType>({
    resolver: zodResolver(accessLoginSchema),
    defaultValues: {
      accessCode: "",
      naitonal: "",
    },
  });

  const handleLogin = (data: AccessLoginSchemaType) => {
    //TODO: Implement login and authentication
    console.log(data);
  };

  return (
    <main className='h-[85vh] grid place-content-center'>
      <Card className='md:w-[500px] w-[350px]'>
        <CardHeader>
          <CardTitle>Login</CardTitle>
          <CardDescription>Login with your institution access code</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form className='space-y-4' onSubmit={form.handleSubmit(handleLogin)}>
              <FormField
                control={form.control}
                name='accessCode'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Access Code</FormLabel>
                    <FormControl>
                      <Input placeholder='Enter your access code' {...field} />
                    </FormControl>
                    <FormDescription>
                      Enter the access code provided from your institution
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name='naitonal'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>National ID</FormLabel>
                    <FormControl>
                      <Input placeholder='Enter your national id number' {...field} />
                    </FormControl>
                    <FormDescription>
                      Enter your personal National ID from left to right in english
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className='flex flex-col'>
                <Button type='submit' className='w-full font-bold text-lg'>
                  Login
                </Button>
                <div className='mt-2 text-center'>
                  <p className='inline -mr-2'>Have an account?</p>
                  <Button variant={"link"} asChild>
                    <Link href={"/login"}>Login with account</Link>
                  </Button>
                </div>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </main>
  );
}
