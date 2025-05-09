"use client";
import React, { useCallback, useMemo, useState } from "react";
import StepsProgress from "./_components/stepsProgress";

import { Button } from "@/components/ui/button";
import VerifyEmailCard from "@/components/verifyEmailCard";
import RegistrationForm from "./_components/registrationForm";
import { Loader2 } from "lucide-react";
import { institutionVerificationService } from "@/apiService/services";
import { useInstitutionRegistrationStore } from "@/store/institutionRegistrationStore";
import { useSearchParams } from "next/navigation";
import Credits from "./_components/credits";

interface StepsLookup {
  [key: number]: {
    title: string;
    description: string;
    component: React.ReactNode;
  };
}

const STEPS = 4;
export default function InstitutionRegisterPage() {
  const { current_step, goBack, setIsVerified, email, verifcationFaildCallback } =
    useInstitutionRegistrationStore();
  const [isPending, setIsPending] = useState(false);
  const params = useSearchParams();
  console.log("params", params);

  const buttonType = useMemo(() => {
    if (current_step === 1) return "submit";
    return "button";
  }, [current_step]);

  const setPendingCallback = useCallback(
    (pending: boolean) => {
      setIsPending(pending);
    },
    [setIsPending]
  );

  const stepsLookup: StepsLookup = {
    1: {
      title: "Institution Name",
      description: "Enter the name of your institution",
      component: <RegistrationForm setIsPending={setPendingCallback} />,
    },
    2: {
      title: "Email Verification",
      description: "Verify your email",
      component: (
        <VerifyEmailCard
          emailToken={email}
          resendVerificationEmail={institutionVerificationService.resendVerificationEmail}
          verifyEmailExists={institutionVerificationService.verifyEmailExists}
          verifyEmail={institutionVerificationService.verifyEmail}
          sucessRedirectionURL={""}
          failureRedirectionURL={""}
          successCallback={setIsVerified}
          failureCallback={verifcationFaildCallback}
        />
      ),
    },
    3: {
      title: "Payment",
      description: "Pay for your institution",
      component: <Credits />,
    },
    4: {
      title: "Payment",
      description: "Pay for your institution",
      component: <h1>Payment Sucess</h1>,
    },
  };

  return (
    <div className='h-full'>
      <div className='w-[50%] mx-auto mt-2'>
        <h1>{current_step}</h1>
        <StepsProgress currentStep={current_step} steps={STEPS} className='mb-12' />
        {stepsLookup[current_step].component}

        <div className='flex justify-between w-full mt-1'>
          <Button disabled={current_step === 1} onClick={goBack}>
            Back
          </Button>
          <Button disabled={isPending} type={buttonType} form='institution-registration-form'>
            {isPending ? <Loader2 className='w-4 h-4 animate-spin' /> : "Next"}
          </Button>
        </div>
      </div>
    </div>
  );
}
