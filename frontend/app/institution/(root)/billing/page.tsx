"use client";
import React, { startTransition, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

// Components
import { Badge } from "@/components/ui/badge";
import CreditsInput from "./_components/creditsInput";

// Actions
import { buyCredits } from "@/actions/payment";

// Services & Hooks
import { getInstitutionCurrentPlan } from "@/apiService/planService";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";

// Utils
import { toast } from "sonner";
import Loader from "@/components/Loader";

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
  if (isLastPlanLoading || !lastPlan) return <Loader />;
  console.log(lastPlan.type);

  return (
    <div>
      <h1>Billing</h1>
      <div className='flex items-center gap-4'>
        <Badge variant={lastPlan.type}>Gold</Badge>
        <h1>{user.credits}</h1>
      </div>

      <CreditsInput name={user.name} email={user.email} planId={lastPlan.id} />
    </div>
  );
}
