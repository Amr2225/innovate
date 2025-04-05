"use client";
import React, { useEffect } from "react";
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

import { REGEXP_ONLY_DIGITS } from "input-otp";
import { Button } from "@/components/ui/button";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { resendEmail, verifyEmail, verifyEmailToken } from "@/api/auth/verifyEmail";
import { Spinner } from "@/components/helpers/Spinner";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";

const OTPSchema = z.object({
  pin: z.string().min(6, {
    message: "Your one-time password must be 6 characters.",
  }),
});

type OTPSchemaType = z.infer<typeof OTPSchema>;

export default function VerifyEmail() {
  const router = useRouter();
  const { token }: { token: string } = useParams();

  const form = useForm<OTPSchemaType>({
    resolver: zodResolver(OTPSchema),
    defaultValues: {
      pin: "",
    },
  });

  const { isLoading, isError } = useQuery({
    queryKey: ["verifyEmailToken"],
    queryFn: () => verifyEmailToken(token),
    retry: 1,
  });

  const { mutate: verifyEmailMutation, isPending } = useMutation({
    mutationFn: (otp: number) => verifyEmail(otp, token),
    onSuccess: () => {
      router.push("/login");
      toast.success("Email verified successfully");
    },
    onError: (e) => {
      toast.error(e.message);
    },
  });

  const { mutate: resendEmailMutation } = useMutation({
    mutationFn: () => resendEmail(undefined, token),
    onSuccess: () => {
      toast.success("Verification email sent");
    },
    onError: (e) => {
      toast.error(e.message);
    },
  });

  useEffect(() => {
    if (isError) {
      router.push("/login");
      toast.error("Resend the verification email");
    }
  }, [isError, router]);

  const handleLogin = (data: OTPSchemaType) => {
    verifyEmailMutation(Number(data.pin));
  };

  if (isLoading) return <LoadingSkeleton />;

  return (
    <div className='h-[85vh] grid place-content-center'>
      <Card className='md:w-[500px] w-[350px]'>
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
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className='h-[85vh] grid place-content-center'>
      <Card className='md:w-[500px] w-[350px]'>
        <CardHeader>
          <Skeleton className='w-full h-10' />
          <Skeleton className='w-full h-10' />
        </CardHeader>
        <CardContent>
          <Skeleton className='w-full h-10' />
          <Skeleton className='w-full h-10' />
          <Skeleton className='w-full h-10' />
          <Skeleton className='w-full h-10' />
        </CardContent>
      </Card>
    </div>
  );
}
