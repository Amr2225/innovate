import { toast } from "sonner";
import { verifyPayment } from "@/actions/verify-payment";
import { useRouter } from "next/navigation";
import { useInstitutionRegistrationStore } from "@/store/institutionRegistrationStore";
import { useEffect, useTransition } from "react";

export default function useVerifyPayment() {
    const router = useRouter();
    const { setStatus, hmac } = useInstitutionRegistrationStore();
    const [isPending, startTransition] = useTransition();


    useEffect(() => {
        if (hmac) {
            console.log("Verify Payment HMAC: ", hmac);
            startTransition(() => {
                verifyPayment(hmac)
                    .then((isVerified) => {
                        setStatus("isPaymentSuccess", isVerified);
                    })
                    .catch(() => {
                        toast.error("Payment Verification Failed Try again later");
                        router.replace("/institution-register");
                    });
            });
        }
    }, [hmac, router, setStatus]);

    return isPending;
}