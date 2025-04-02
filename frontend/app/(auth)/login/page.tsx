"use client";
import React, { startTransition, useActionState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";

// Server Actions
import { login } from "@/actions/login";

// Assets
import LoginImage from "../../../assets/login.png";
import googleIcon from "../../../assets/googleIcons.png";
import Image from "next/image";

// Components
import LoginErrorMessage from "@/components/helpers/LoginErrorMessage";
import { zodResolver } from "@hookform/resolvers/zod";
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

import { signIn } from "next-auth/react";

// Types & Schemas
import { LoginError } from "@/types/auth.type";
import { LoginSchema, LoginSchemaType } from "@/schema/loginSchema";
import { DEFAULT_LOGIN_REDIRECT } from "@/routes";

export default function Login() {
  const [error, submitAction, isPending] = useActionState<LoginError, LoginSchemaType>(
    async (prev, data) => {
      const status = await login(data);

      if (status) return { message: status.message, type: status.type };

      return { message: "" };
    },
    { message: "" }
  );

  const form = useForm<LoginSchemaType>({
    resolver: zodResolver(LoginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const handleLogin = (data: LoginSchemaType) => {
    console.log(data);
    startTransition(() => submitAction(data));
  };

  const hanldeGoogleLogin = () => {
    signIn("google", { redirectTo: DEFAULT_LOGIN_REDIRECT });
    console.log("google in");
  };

  return (
    <div className='flex justify-start items-center h-[88.5vh]'>
      <div className='h-full aspect-square hidden md:block'>
        <Image src={LoginImage} alt='Login image' className='h-full' />
      </div>
      <div className='md:w-[40%] mx-auto'>
        <h1 className='font-bold text-3xl mb-10 text-center'>Login to your account</h1>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleLogin)} className='space-y-4'>
            <FormField
              control={form.control}
              name='email'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input placeholder='Enter your email' {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name='password'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Password</FormLabel>
                  <FormControl>
                    <Input placeholder='Enter your password' {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type='submit' className='w-full font-bold text-lg' disabled={isPending}>
              Login
            </Button>
            <LoginErrorMessage error={error} />
            <div className='mt-1 text-center'>
              <p className='inline -mr-2'>Don&apos;t have an account?</p>
              <Button variant={"link"} asChild>
                <Link href={"/login-access"}>Login with access code</Link>
              </Button>
            </div>
          </form>
          <div className='mt-7'>
            <span className='w-full bg-neutral-300 h-[3px] block relative'>
              <p className='absolute top-[50%] left-[50%] -translate-x-[50%] -translate-y-[50%] bg-white px-3 uppercase text-neutral-500 text-sm'>
                or login with
              </p>
            </span>

            <div
              className='border border-neutral-300 h-[50px] mt-5 md:w-[70%] mx-auto flex cursor-pointer hover:bg-neutral-100/90 hover:scale-95 transition-all '
              onClick={hanldeGoogleLogin}
            >
              <div className='border-r border-neutral-300 mr-3 px-3 flex items-center'>
                <Image src={googleIcon} alt='google icon' />
              </div>
              <h1 className='flex items-center'>Google</h1>
            </div>
          </div>
        </Form>
      </div>
    </div>
  );
}
