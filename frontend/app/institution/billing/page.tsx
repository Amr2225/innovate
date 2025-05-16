"use client";
import { Badge } from "@/components/ui/badge";
import React, { startTransition, useEffect } from "react";
import CreditsInput from "./_components/creditsInput";
import { useAuth } from "@/hooks/useAuth";
import { toast } from "sonner";
import { buyCredits } from "@/actions/payment";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";

export default function Page() {
  const { user, updateUser } = useAuth();
  const searchParams = useSearchParams();
  const hmac = searchParams.get("hmac");
  const router = useRouter();

  useEffect(() => {
    if (hmac && user) {
      startTransition(async () => {
        const isPaymentVerified = await buyCredits(hmac);
        if (isPaymentVerified.isSuccess) {
          toast.success("Payment successful");
          updateUser();
        } else {
          toast.error(isPaymentVerified.message || "Payment failed");
        }
        router.replace("/institution/billing");
      });
    }
  }, [hmac, user, updateUser, router]);

  if (!user) return null;

  return (
    <div>
      <h1>Billing</h1>
      <div className='flex items-center gap-4'>
        <Badge variant='gold'>Gold</Badge>
        <h1>{user.credits}</h1>
      </div>

      <CreditsInput name={user.name} email={user.email} />
      <Button onClick={() => updateUser()}>Update User</Button>
    </div>
  );
}
