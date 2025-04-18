"use client";
import React, { useState, useTransition } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
  FormDescription,
  FormLabel,
} from "@/components/ui/form";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import Link from "next/link";

import { useForm } from "react-hook-form";
import { loginAccessSchema, LoginAccessSchemaType } from "@/schema/loginAccessSchema";
import { zodResolver } from "@hookform/resolvers/zod";
import { loginAccess } from "@/actions/login-access";
import { LoginError } from "@/types/auth.type";
import { redirect } from "next/navigation";
import { firstLoginRoutes } from "@/routes";

export default function AccessLogin() {
  const [error, setError] = useState<LoginError | null>(null);
  const [isPending, startTransition] = useTransition();

  const form = useForm<LoginAccessSchemaType>({
    resolver: zodResolver(loginAccessSchema),
    defaultValues: {
      accessCode: "",
      nationalId: "",
    },
  });

  const handleLogin = (data: LoginAccessSchemaType) => {
    console.log(data);
    startTransition(() => {
      loginAccess(data).then((data) => {
        console.log(data);
        if (data?.error) setError({ message: data.error, type: data.type });
        else if (data?.isFirstLogin) redirect(firstLoginRoutes[0]);
        else if (data?.role) redirect(`/${data.role.toLowerCase()}/dashboard`);
      });
    });
  };

  return (
    <div className='h-[85vh] grid place-content-center'>
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
                name='nationalId'
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
                <Button disabled={isPending} type='submit' className='w-full font-bold text-lg'>
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
            {error?.message && <p className='text-red-500 text-center'>{error.message}</p>}
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
