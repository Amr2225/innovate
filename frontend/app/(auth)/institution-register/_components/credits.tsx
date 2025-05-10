"use client";
import React, { useMemo, useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Label } from "@radix-ui/react-label";
import { Input } from "@/components/ui/input";
// import { Button } from "@/components/ui/button";
import { useMutation } from "@tanstack/react-query";
import { AxiosError } from "axios";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { paymentService } from "@/apiService/services";
import { useInstitutionRegistrationStore } from "@/store/institutionRegistrationStore";
// import { useInstitutionRegistrationStore } from "@/store/institutionRegistrationStore";

const planId = "b784f4f9-7734-46f9-854c-4f641060a361";
export default function Credits({ setIsPending }: { setIsPending: (isPending: boolean) => void }) {
  const [credits, setCredits] = useState<number>(0);
  const { email, name } = useInstitutionRegistrationStore();

  const { mutate: purchaseCredits } = useMutation({
    mutationFn: () =>
      paymentService.generatePaymentLink({
        credits: credits,
        plan_id: planId,
        name: name,
        email: email,
      }),
    onSuccess: (url) => {
      window.location.href = url;
    },
    onError: (error) => {
      setIsPending(false);
      if (error instanceof AxiosError) {
        toast.error(error.response?.data.errors || "Something went wrong, please try again");
      }
    },
    onSettled: () => {
      setIsPending(false);
    },
  });

  const totalCredits = useMemo(() => {
    return credits * 2;
  }, [credits]);

  const handlePurchaseCredits = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (credits === 0) {
      toast.error("Please Enter Credits Amount");
      return;
    }
    setIsPending(true);
    purchaseCredits();
  };

  return (
    <form onSubmit={handlePurchaseCredits} id='credits-form'>
      <div className='flex flex-col md:flex-row justify-center gap-5 items-center h-full md:h-[250px]'>
        <Card className='w-full min-h-full'>
          <CardHeader>
            <CardTitle>Credits</CardTitle>
            <CardDescription>Enter the amount of credits you want to purchase</CardDescription>
          </CardHeader>
          <CardContent>
            <Label htmlFor='credits'>Credits</Label>
            <Input
              type='text'
              id='credits'
              value={credits || ""}
              onChange={(e) => setCredits(+e.target.value)}
              className='[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none'
            />
          </CardContent>
        </Card>

        <Card className='w-full min-h-full'>
          <CardHeader>
            <CardTitle>Payment Details</CardTitle>
            <CardDescription>Total amount to pay</CardDescription>
          </CardHeader>
          <CardContent className='space-y-2 text-sm'>
            <div className='flex justify-between items-center'>
              <h2 className='font-semibold '>Plan</h2>
              <Badge className='py-1' variant='gold'>
                Gold
              </Badge>
            </div>

            <div className='flex justify-between items-center'>
              <h2 className='font-semibold '>Credit Value</h2>
              <p>2.00 EGP</p>
            </div>

            <div className='flex justify-between items-center'>
              <h2 className='font-semibold'>Credits</h2>
              <p>{credits}</p>
            </div>

            <span className='w-full border border-dashed border-neutral-400 block' />
            <div className='flex justify-between items-center'>
              <h2 className='font-semibold'>Total</h2>
              <p>{totalCredits} EGP</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </form>
  );
}
