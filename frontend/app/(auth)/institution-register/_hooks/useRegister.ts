import { useEffect, useCallback, useTransition } from "react";
import { institutionRegister } from "@/actions/register";

import { useInstitutionRegistrationStore } from "@/store/institutionRegistrationStore";
import { toast } from "sonner";

export default function useRegister({ logo }: { logo: File | null }) {
    const { isPaymentSuccess, name, email, password, confirm_password, credits, reset, hmac, setStatus } = useInstitutionRegistrationStore()
    const [isPending, startTransition] = useTransition();


    const handleRegistration = useCallback(async () => {
        if (!isPaymentSuccess || !hmac) return;

        startTransition(async () => {
            const formData = new FormData();
            formData.append("name", name);
            formData.append("email", email);
            formData.append("password", password);
            formData.append("confirm_password", confirm_password);
            formData.append("credits", credits.toString());
            formData.append("hmac", hmac);
            console.log("Logo Instance of", logo instanceof File);

            if (logo instanceof File) {
                formData.append("logo", logo);
            }

            const res = await institutionRegister(formData);
            if (!res) {
                toast.error("Registration Failed")
                reset();
                return;
            }

            if (res.isSuccess) {
                toast.success("Registration successful!");
                setStatus("isRegistrationSuccess", true);
            } else {
                toast.error(res.error);
                setStatus("isRegistrationSuccess", false);
                console.log("Registration Failed", res);
                reset();
            }
        });

    }, [isPaymentSuccess, hmac, name, email, password, confirm_password, credits, logo, reset, setStatus]);

    useEffect(() => {
        if (isPaymentSuccess) {
            handleRegistration();
        }
    }, [isPaymentSuccess, handleRegistration]);

    return isPending;
}