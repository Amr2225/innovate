"use client";
import React, { useState } from "react";
import { resendEmail } from "@/api/auth/verifyEmail";
import { Spinner } from "@/components/helpers/Spinner";
import { Button } from "@/components/ui/button";
import { Card, CardTitle, CardHeader, CardDescription, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
// import { Form, useForm } from "react-hook-form";
import { z } from "zod";
// import { zodResolver } from "@hookform/resolvers/zod";
// import { FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form";
import { cn } from "@/lib/utils";

export default function VerifyEmailPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const { mutate: resendEmailMutation, isPending } = useMutation({
    mutationFn: () => resendEmail(email),
    onSuccess: (token) => {
      router.push(`/verify-email/${token}`);
    },
    onError: (e) => {
      console.log(e);
      toast.error(e.message);
    },
  });

  const handleSubmit = () => {
    setError("");

    const emailSchema = z.string().email({ message: "Invalid email" });
    const { success, error } = emailSchema.safeParse(email);

    if (!success) {
      console.log(error);
      setError("Invalid email");
      return;
    }

    resendEmailMutation();
  };

  return (
    <div className='h-[85vh] grid place-content-center'>
      <Card className='md:w-[500px] w-[350px]'>
        <CardHeader>
          <CardTitle>Verify Email</CardTitle>
          <CardDescription>Enter Your Email to Verify</CardDescription>
        </CardHeader>
        <CardContent className='space-y-4'>
          <div className='space-y-1'>
            <label htmlFor='email'>Email</label>
            <Input
              id='email'
              placeholder='Enter your email'
              className={cn({ "border-red-500": error })}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            {error && <p className='text-red-500 text-sm'>{error}</p>}
          </div>

          <div className='flex flex-col'>
            <Button
              type='button'
              className='w-full font-bold text-base'
              onClick={() => handleSubmit()}
            >
              {isPending ? (
                <div className='flex items-center gap-2'>
                  <Spinner size='small' className='text-white' />
                  Verifying...
                </div>
              ) : (
                "Verify"
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
