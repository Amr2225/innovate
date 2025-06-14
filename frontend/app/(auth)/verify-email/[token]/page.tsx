"use client";
import React from "react";
import { useParams } from "next/navigation";

// Components
import VerifyEmailCard from "@/components/verifyEmailCard";

// Services
import { userVerificationService } from "@/apiService/services";

export default function VerifyEmail() {
  const { token }: { token: string } = useParams();

  return (
    <div className='h-[85vh] grid place-content-center'>
      <VerifyEmailCard
        emailToken={token}
        resendVerificationEmail={userVerificationService.resendVerificationEmail}
        verifyEmailExists={userVerificationService.verifyEmailExists}
        verifyEmail={userVerificationService.verifyEmail}
        sucessRedirectionURL={"/login"}
        failureRedirectionURL={"/login"}
      />
    </div>
  );
}
