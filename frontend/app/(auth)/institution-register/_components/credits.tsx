"use client";
import React, { useMemo, useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Label } from "@radix-ui/react-label";
import { Input } from "@/components/ui/input";
// import { Button } from "@/components/ui/button";
import { useMutation, useQuery } from "@tanstack/react-query";
import { AxiosError } from "axios";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { paymentService } from "@/apiService/services";
import { useInstitutionRegistrationStore } from "@/store/institutionRegistrationStore";
import { getPlanDetails } from "@/apiService/planService";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { z } from "zod";

export default function Credits({
  setIsPending,
  planId,
}: {
  setIsPending: (isPending: boolean) => void;
  planId: string;
}) {
  const [newCredits, setNewCredits] = useState<number>(0);
  const { email, name, setCredits, reset } = useInstitutionRegistrationStore();
  const router = useRouter();

  const { mutate: purchaseCredits } = useMutation({
    mutationFn: () =>
      paymentService.generatePaymentLink({
        credits: newCredits,
        plan_id: planId,
        name: name,
        email: email,
      }),
    onSuccess: (url) => {
      setCredits(newCredits);
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

  const {
    data: plan,
    isLoading: isPlanLoading,
    isError,
  } = useQuery({
    queryKey: [`plan-${planId}`],
    queryFn: () => getPlanDetails(planId),
    enabled: !!planId,
  });

  const totalCredits = useMemo(() => {
    if (plan) {
      return newCredits * +plan.credit_price;
    }
    return 0;
  }, [newCredits, plan]);

  const handlePurchaseCredits = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (newCredits === 0) {
      toast.error("Please Enter Credits Amount");
      return;
    }
    if (!validateCredits(newCredits)) return;
    setIsPending(true);
    purchaseCredits();
  };

  if (isPlanLoading)
    return (
      <div className='flex justify-center items-center h-full'>
        <Loader2 className='w-10 h-10 animate-spin text-primary' />
      </div>
    );

  if (isError || !plan) {
    toast.error("Invalid Plan");
    reset();
    router.push("/");
    return null;
  }

  const createCreditsSchema = (planType: "Silver" | "Gold" | "Diamond") => {
    return z
      .number()
      .min(1, "Credits must be at least 1")
      .min(plan.minimum_credits, {
        message: `Minimum credits for ${planType} plan is ${plan.minimum_credits.toLocaleString()}`,
      })
      .refine((value) => !isNaN(value) && value > 0, "Please enter a valid number of credits");
  };

  const validateCredits = (credits: number) => {
    const schema = createCreditsSchema(plan.type);
    const result = schema.safeParse(credits);
    if (!result.success) {
      toast.error(result.error.errors[0].message);
      return false;
    }
    return true;
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
              value={newCredits || ""}
              onChange={(e) => setNewCredits(+e.target.value)}
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
              <Badge className='py-1' variant={plan.type}>
                {plan.type}
              </Badge>
            </div>

            <div className='flex justify-between items-center'>
              <h2 className='font-semibold '>Credit Price</h2>
              <p>
                {plan.credit_price} {plan.currency}
              </p>
            </div>

            <div className='flex justify-between items-center'>
              <h2 className='font-semibold'>Credits</h2>
              <p>{newCredits.toLocaleString()}</p>
            </div>

            <span className='w-full border border-dashed border-neutral-400 block' />
            <div className='flex justify-between items-center'>
              <h2 className='font-semibold'>Total</h2>
              <p>{totalCredits.toLocaleString()} EGP</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </form>
  );
}
