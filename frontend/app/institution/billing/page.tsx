"use client";
import React, { startTransition, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

// Components
import { Badge } from "@/components/ui/badge";
import CreditsInput from "./_components/creditsInput";

// Actions
import { buyCredits } from "@/actions/payment";
import { Button } from "@/components/ui/button";

// Services & Hooks
import { getInstitutionCurrentPlan } from "@/apiService/planService";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";

//Icons
import { Loader2 } from "lucide-react";
// Utils
import { toast } from "sonner";

export default function Page() {
  const { user, updateUser } = useAuth();
  const searchParams = useSearchParams();
  const hmac = searchParams.get("hmac");
  const router = useRouter();

  const { data: lastPlan, isLoading: isLastPlanLoading } = useQuery({
    queryKey: ["institution-last-plan"],
    queryFn: () => getInstitutionCurrentPlan(),
  });

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
  if (isLastPlanLoading || !lastPlan)
    return (
      <div className='flex items-center justify-center h-screen'>
        <Loader2 className='w-10 h-10 animate-spin' />
      </div>
    );

  console.log(lastPlan);

  return (
    <div>
      <h1>Billing</h1>
      <div className='flex items-center gap-4'>
        <Badge variant={lastPlan.type}>Gold</Badge>
        <h1>{user.credits}</h1>
      </div>

      <CreditsInput name={user.name} email={user.email} planId={lastPlan.id} />
      <Button onClick={() => updateUser()}>Update User</Button>
    </div>
  );
}
