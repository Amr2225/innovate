"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { z } from "zod";

// Components
import { Spinner } from "@/components/helpers/Spinner";
import { Button } from "@/components/ui/button";
import { Card, CardTitle, CardHeader, CardDescription, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

// Utils
import { cn } from "@/lib/utils";

// Services & Hooks
import { useMutation } from "@tanstack/react-query";
import { userVerificationService } from "@/apiService/services";
import { toast } from "sonner";

export default function VerifyEmailPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const { mutate: resendEmailMutation, isPending } = useMutation({
    mutationFn: () => userVerificationService.resendVerificationEmail(undefined, email),
    onSuccess: (token) => {
      router.push(`/verify-email/${token}`);
    },
    onError: (e) => {
      toast.error(e.message);
    },
  });

  const handleSubmit = () => {
    setError("");

    const emailSchema = z.string().email({ message: "Invalid email" });
    const { success } = emailSchema.safeParse(email);

    if (!success) {
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
