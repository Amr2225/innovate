"use client";
import { useRouter, useSearchParams } from "next/navigation";
import React from "react";

export default function page() {
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const searchParams = useSearchParams();
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const router = useRouter();
  // eslint-disable-next-line react-hooks/rules-of-hooks
  React.useEffect(() => {
    if (searchParams.toString()) {
      router.replace(`/payment/`);
    }
  }, [searchParams, router]);
  console.log("Payment token:", searchParams);
  return <div>Payment</div>;
}
