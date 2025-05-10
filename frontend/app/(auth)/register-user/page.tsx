"use client";
import React, { startTransition, useActionState } from "react";
import Link from "next/link";

import registerImage from "@/assets/register.png";
import googleIcon from "../../../assets/googleIcons.png";
import Image from "next/image";

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

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import DatePicker from "@/components/date-picker";
import { RegisterSchemaType, RegisterSchema } from "@/schema/registerSchema";

//Server Actions
import { register, RegisterResponse } from "@/actions/register";
// import { FormSuccess } from "@/components/helpers/FormSucess";
import { logout } from "@/lib/session";
import { redirect } from "next/navigation";
import LoginErrorMessage from "@/components/helpers/LoginErrorMessage";

export default function RegisterUser() {
  const [state, submitAction, isPending] = useActionState<RegisterResponse, RegisterSchemaType>(
    async (prev, data) => {
      const res = await register(data);
      if (res?.error) return { error: res.error };
      if (res?.token) {
        logout();
        redirect(`/verify-email/${res.token}`);
      }
      return { error: "User registered successfully, login now" };
    },
    { error: "", token: "" }
  );

  const form = useForm<RegisterSchemaType>({
    resolver: zodResolver(RegisterSchema),
    defaultValues: {
      first_name: "",
      middle_name: "",
      last_name: "",
      email: "",
      password: "",
      confirm_password: "",
      // birth_date: "",
    },
  });

  const handleRegister = (data: RegisterSchemaType) => {
    console.log(data);
    startTransition(() => submitAction(data));
  };

  const hanldeGoogleLogin = () => {
    console.log("google in");
  };

  return (
    <div className='flex justify-start items-center h-[88.5vh]'>
      <div className='h-full aspect-square hidden md:block'>
        <Image src={registerImage} alt='Login image' className='h-full' />
      </div>
      <div className='md:w-[40%] mx-auto'>
        <h1 className='font-bold text-3xl mb-10 text-center'>Complete Registeration</h1>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleRegister)} className='space-y-4'>
            <h5 className='-mb-1 '>Full Name</h5>
            <div className='flex flex-row gap2 justify-between items-center '>
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
            </div>

            <FormField
              control={form.control}
              name='birth_date'
              render={({ field: { value, onChange } }) => (
                <FormItem>
                  <FormLabel>Birth Date</FormLabel>
                  <FormControl>
                    <DatePicker date={value} setDate={onChange} />
                    {/* <Input placeholder='Last Name' {...field} /> */}
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
                    <Input placeholder='Enter your password' {...field} type='password' />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name='confirm_password'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Confirm Password</FormLabel>
                  <FormControl>
                    <Input placeholder='Confirm Password' {...field} type='password' />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type='submit' disabled={isPending} className='w-full font-bold text-lg'>
              Register
            </Button>
            <div className='mt-1 text-center'>
              <p className='inline -mr-2'>Have an account?</p>
              <Button variant={"link"} asChild>
                <Link href={"/login"}>Login to your account</Link>
              </Button>
            </div>
          </form>
          <LoginErrorMessage error={{ message: state.error }} />
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
      {/* {error.message && <p className='text-red-500'>{error.message}</p>} */}
    </div>
  );
}
