"use client";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams, useParams, useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";

// Components
import { Button } from "@/components/ui/button";
import VerifyEmailCard from "@/components/verifyEmailCard";

// Local Components
import StepsProgress from "../_components/stepsProgress";
import RegistrationForm from "../_components/registrationForm";
import Credits from "../_components/credits";
import { RegistrationVerification } from "../_components/verifyRegistration";

// Icons
import { Loader2 } from "lucide-react";

// Services & Actions
import { institutionVerificationService } from "@/apiService/services";

// Store
import { useInstitutionRegistrationStore } from "@/store/institutionRegistrationStore";

// Hooks
import useRegister from "../_hooks/useRegister";
import useVerifyPayment from "../_hooks/useVerifyPayment";

interface StepsLookup {
  [key: number]: {
    title: string;
    description: string;
    component: React.ReactNode;
  };
}

type NextButton = {
  text: string;
  type: "submit" | "button";
  disabled: boolean;
  formId: string;
};

const STEPS = 4;
export default function InstitutionRegisterPage() {
  const {
    current_step,
    goBack,
    verficationFailedCallback,
    setStatus,
    setHmac,
    isPaymentSuccess,

    email,
    getFile,
  } = useInstitutionRegistrationStore();
  const searchParams = useSearchParams();
  const router = useRouter();

  const [isPending, setIsPending] = useState(false);
  const [logo, setLogo] = useState<File | null>(null);
  const { planId }: { planId: string } = useParams();

  const hmac = useMemo(() => searchParams.get("hmac"), [searchParams]);

  useEffect(() => {
    const loadFile = async () => {
      const file = await getFile();
      setLogo(file);
    };
    loadFile();
  }, [getFile]);

  // Remove all query parameters without refresh
  useEffect(() => {
    //     // Remove all query parameters without refresh
    //     const newUrl = new URL(window.location.href);
    //     newUrl.search = "";
    //     window.history.replaceState({}, "", newUrl.toString());
    if (hmac) {
      const path = window.location.pathname;
      router.replace(path, { scroll: false });
      setHmac(hmac);
    }
  }, [hmac, setHmac, router]);

  // Verify payment
  const isVerifyingPayment = useVerifyPayment();

  // Handle registration callback
  const isRegistering = useRegister({ logo });

  const setPendingCallback = useCallback(
    (pending: boolean) => {
      setIsPending(pending);
    },
    [setIsPending]
  );

  const nextButton = useMemo<NextButton>(() => {
    switch (current_step) {
      case 1:
        return { text: "Next", type: "submit", disabled: isPending, formId: "registration-form" };
      case 2:
        return { text: "Next", type: "button", disabled: true, formId: "" };
      case 3:
        return { text: "Pay", type: "submit", disabled: isPending, formId: "credits-form" };
      case 4:
        return { text: "Redirecting...", type: "button", disabled: true, formId: "" };
      default:
        return { text: "Next", type: "button", disabled: isPending, formId: "" };
    }
  }, [current_step, isPending]);

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
          successCallback={() => setStatus("isEmailVerified", true)}
          failureCallback={verficationFailedCallback}
        />
      ),
    },
    3: {
      title: "Credits",
      description: "Enter the amount of credits you want to purchase",
      component: <Credits setIsPending={setPendingCallback} planId={planId} />,
    },
    4: {
      title: "Payment",
      description: "Pay for your institution",
      component: (
        <RegistrationVerification isRegistrationSuccess={isPaymentSuccess} planId={planId} />
      ),
    },
  };

  return (
    <div className='h-full'>
      <div className='lg:w-[50%] md:w-[70%] w-[90%] mx-auto mt-2'>
        {logo?.name} {logo instanceof File ? "true" : "false"}
        <StepsProgress currentStep={current_step} steps={STEPS} className='mb-5 md:mb-12' />
        <AnimatePresence mode='wait'>
          <motion.div
            key={current_step}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5, ease: "easeInOut" }}
          >
            {isVerifyingPayment || isRegistering ? (
              <div className='flex justify-center items-center h-full'>
                <Loader2 className='w-10 h-10 animate-spin text-primary' />
              </div>
            ) : (
              stepsLookup[current_step].component
            )}
          </motion.div>
        </AnimatePresence>
        <div className='flex justify-between w-full mt-3'>
          <Button disabled={current_step === 1} onClick={goBack}>
            {current_step === 3 ? "Reset" : "Back"}
          </Button>
          <Button disabled={nextButton.disabled} type={nextButton.type} form={nextButton.formId}>
            {isPending ? <Loader2 className='w-4 h-4 animate-spin' /> : nextButton.text}
          </Button>
        </div>
      </div>
    </div>
  );
}
