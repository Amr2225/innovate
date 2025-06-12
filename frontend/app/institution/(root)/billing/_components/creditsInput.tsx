"use client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import React, { useCallback, useState, useTransition } from "react";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import { paymentService } from "@/apiService/services";
import { Label } from "@/components/ui/label";

export default function CreditsInput({
  name,
  email,
  planId,
  minimumCredits = 0,
}: {
  name: string;
  email: string;
  planId: string;
  minimumCredits?: number;
}) {
  const [credits, setCredits] = useState(0);

  const [isPending, startTransition] = useTransition();

  // Generate payment link
  const handleBuyCredits = useCallback(async () => {
    if (credits <= 0) {
      toast.error("Please enter credits amount");
      return;
    }

    if (credits < minimumCredits) {
      toast.error(`Minimum credits amount is ${minimumCredits}`);
      return;
    }

    startTransition(async () => {
      paymentService
        .generatePaymentLink({
          name: name,
          email: email,
          plan_id: planId,
          credits: credits,
          redirection_url: window.location.href,
        })
        .then((url) => {
          window.location.href = url;
        })
        .catch((err) => {
          console.log("Error", err);
          toast.error(err.response.data.errors);
        });
    });
  }, [credits, email, minimumCredits, name, planId]);

  return (
    <div>
      <Label>Credits</Label>
      <Input
        type='number'
        value={credits || ""}
        onChange={(e) => setCredits(+e.target.value)}
        placeholder='Enter credits amount'
      />
      <Button onClick={handleBuyCredits} disabled={isPending} className='mt-4'>
        {isPending ? <Loader2 className='w-4 h-4 animate-spin' /> : "Buy Credits"}
      </Button>
    </div>
  );
}
