"use client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import React, { useCallback, useState, useTransition } from "react";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import { paymentService } from "@/apiService/services";

const planId = "b784f4f9-7734-46f9-854c-4f641060a361";
export default function CreditsInput({ name, email }: { name: string; email: string }) {
  const [credits, setCredits] = useState(0);

  const [isPending, startTransition] = useTransition();

  // Generate payment link
  const handleBuyCredits = useCallback(async () => {
    if (credits <= 0) {
      toast.error("Please enter credits amount");
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
          toast.error(err.message);
        });
    });
  }, [credits, email, name]);

  return (
    <div>
      <Input type='number' value={credits || ""} onChange={(e) => setCredits(+e.target.value)} />
      <Button onClick={handleBuyCredits} disabled={isPending}>
        {isPending ? <Loader2 className='w-4 h-4 animate-spin' /> : "Buy Credits"}
      </Button>
    </div>
  );
}
