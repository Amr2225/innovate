"use client";
import React, { useCallback, useEffect, useMemo, useState, useTransition } from "react";
import { useSearchParams } from "next/navigation";

// Components
import { Button } from "@/components/ui/button";
import VerifyEmailCard from "@/components/verifyEmailCard";
import { Card } from "@/components/ui/card";

// Local Components
import StepsProgress from "./_components/stepsProgress";
import RegistrationForm from "./_components/registrationForm";
import Credits from "./_components/credits";
import { PaymentVerification } from "./_components/verifyPayment";

// Icons
import { Loader2 } from "lucide-react";

// Services & Actions
import { institutionVerificationService } from "@/apiService/services";
import { verifyPayment } from "@/actions/verify-payment";

// Store
import { useInstitutionRegistrationStore } from "@/store/institutionRegistrationStore";

interface StepsLookup {
  [key: number]: {
    title: string;
    description: string;
    component: React.ReactNode;
  };
}

const STEPS = 4;
export default function InstitutionRegisterPage() {
  const {
    current_step,
    goBack,
    setIsVerified,
    email,
    verifcationFaildCallback,
    setIsPaymentSuccess,
    is_payment_success,
  } = useInstitutionRegistrationStore();
  const [isVerifyingPayment, startTransition] = useTransition();

  const [isPending, setIsPending] = useState(false);
  const params = useSearchParams();

  const hmac = useMemo(() => params.get("hmac"), [params]);

  useEffect(() => {
    if (hmac) {
      startTransition(() => {
        verifyPayment(hmac, {}).then((isVerified) => {
          setIsPaymentSuccess(isVerified);
        });
      });
    }
  }, [hmac, setIsPaymentSuccess]);

  const setPendingCallback = useCallback(
    (pending: boolean) => {
      setIsPending(pending);
    },
    [setIsPending]
  );

  const nextButton = useMemo<{
    text: string;
    type: "submit" | "button";
    disabled: boolean;
    formId: string;
  }>(() => {
    if (current_step === 1)
      return {
        text: "Next",
        type: "submit",
        disabled: isPending,
        formId: "institution-registration-form",
      };
    if (current_step === 2) return { text: "Next", type: "button", disabled: true, formId: "" };
    if (current_step === 3)
      return { text: "Pay", type: "submit", disabled: isPending, formId: "credits-form" };
    if (current_step === 4)
      return { text: "Redirecting...", type: "button", disabled: true, formId: "" };
    return { text: "Next", type: "button", disabled: isPending, formId: "" };
  }, [current_step, isPending]);

  if (isVerifyingPayment) {
    return (
      <Card className='flex flex-col gap-8 py-3 justify-center w-[50%] mx-auto items-center h-full'>
        <Loader2 size={80} className='animate-spin' />
        <p className='text-xl text-center'>Please Wait Verifying payment...</p>
      </Card>
    );
  }

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
      title: "Credits",
      description: "Enter the amount of credits you want to purchase",
      component: <Credits setIsPending={setPendingCallback} />,
    },
    4: {
      title: "Payment",
      description: "Pay for your institution",
      component: <PaymentVerification isPaymentSuccess={is_payment_success} />,
    },
  };

  return (
    <div className='h-full'>
      <div className='lg:w-[50%] md:w-[70%] w-[90%] mx-auto mt-2'>
        <StepsProgress currentStep={current_step} steps={STEPS} className='mb-5 md:mb-12' />
        {stepsLookup[current_step].component}

        <div className='flex justify-between w-full mt-3'>
          <Button disabled={current_step === 1} onClick={goBack}>
            Back
          </Button>
          <Button disabled={nextButton.disabled} type={nextButton.type} form={nextButton.formId}>
            {isPending ? <Loader2 className='w-4 h-4 animate-spin' /> : nextButton.text}
          </Button>
        </div>
      </div>
    </div>
  );
}
