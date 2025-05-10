"use client";
import React from "react";

// Components
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
  FormDescription,
} from "@/components/ui/form";
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
  InputOTPSeparator,
} from "@/components/ui/input-otp";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/helpers/Spinner";
import { Skeleton } from "@/components/ui/skeleton";
import { REGEXP_ONLY_DIGITS } from "input-otp";

// Hooks
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import useVerifyEmailQuery from "@/queryHooks/verfyEmailQuery";

// API Services
import { IVerifyEmail } from "@/apiService/verificationService";

// Schema
import { OTPSchema, OTPSchemaType } from "@/schema/OTPSchema";

export interface VerifyEmailQueryProps extends IVerifyEmail {
  emailToken: string;
  sucessRedirectionURL: string;
  failureRedirectionURL: string;
  successCallback?: () => void;
  failureCallback?: () => void;
}

export default function VerifyEmailCard({
  emailToken,
  resendVerificationEmail,
  verifyEmailExists,
  verifyEmail,
  sucessRedirectionURL,
  failureRedirectionURL,
  successCallback,
  failureCallback,
}: VerifyEmailQueryProps) {
  const form = useForm<OTPSchemaType>({
    resolver: zodResolver(OTPSchema),
    defaultValues: {
      pin: "",
    },
  });

  const { verifyEmailMutation, isPending, isLoading, resendEmailMutation } = useVerifyEmailQuery({
    emailToken,
    resendVerificationEmail,
    verifyEmailExists,
    verifyEmail,
    sucessRedirectionURL,
    failureRedirectionURL,
    successCallback,
    failureCallback,
  });

  if (isLoading) return <LoadingSkeleton />;

  const handleLogin = (data: OTPSchemaType) => {
    verifyEmailMutation(Number(data.pin));
  };

  return (
    <Card className='md:w-[500px] w-[350px] mx-auto'>
      <CardHeader>
        <CardTitle>Verify Email</CardTitle>
        <CardDescription>One-Time Password</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form className='space-y-4' onSubmit={form.handleSubmit(handleLogin)}>
            <FormField
              control={form.control}
              name='pin'
              render={({ field }) => (
                <FormItem className='mx-auto w-fit text-center'>
                  <FormControl>
                    <InputOTP maxLength={6} {...field} pattern={REGEXP_ONLY_DIGITS}>
                      <InputOTPGroup className='[&>div]:w-12 [&>div]:h-12'>
                        <InputOTPSlot index={0} />
                        <InputOTPSlot index={1} />
                        <InputOTPSlot index={2} />
                      </InputOTPGroup>
                      <InputOTPSeparator />
                      <InputOTPGroup className='[&>div]:w-12 [&>div]:h-12'>
                        <InputOTPSlot index={3} />
                        <InputOTPSlot index={4} />
                        <InputOTPSlot index={5} />
                      </InputOTPGroup>
                    </InputOTP>
                  </FormControl>
                  <FormDescription>
                    Please enter the one-time password sent to your email.
                  </FormDescription>
                  <Button
                    variant='link'
                    className='text-neutral-600'
                    type='button'
                    onClick={() => resendEmailMutation()}
                  >
                    Resend OTP
                  </Button>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className='flex flex-col'>
              <Button type='submit' className='w-full font-bold text-base' disabled={isPending}>
                {isPending ? (
                  <div className='flex items-center gap-2'>
                    <Spinner size='small' className='text-white' />
                    Submitting...
                  </div>
                ) : (
                  "Submit"
                )}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}

function LoadingSkeleton() {
  return (
    <Card className='md:w-[500px] w-[350px] mx-auto'>
      <CardHeader>
        <Skeleton className='w-full h-10' />
        <Skeleton className='w-full h-5' />
      </CardHeader>
      <CardContent>
        <div className='mx-auto w-fit'>
          <InputOTP maxLength={6} pattern={REGEXP_ONLY_DIGITS}>
            <InputOTPGroup className='[&>div]:w-12 [&>div]:h-12 gap-1'>
              <Skeleton className='size-20' />
              <Skeleton className='size-20' />
              <Skeleton className='size-20' />
            </InputOTPGroup>
            <InputOTPSeparator />
            <InputOTPGroup className='[&>div]:w-12 [&>div]:h-12 gap-1'>
              <Skeleton className='size-20' />
              <Skeleton className='size-20' />
              <Skeleton className='size-20' />
            </InputOTPGroup>
          </InputOTP>
        </div>
        <Skeleton className='w-full h-10 mt-10' />
      </CardContent>
    </Card>
  );
}
