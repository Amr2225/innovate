import { useEffect, useCallback, useTransition } from "react";
import { institutionRegister } from "@/actions/register";

import { useInstitutionRegistrationStore } from "@/store/institutionRegistrationStore";
import { toast } from "sonner";
import { getImage } from "@/store/imageStorage";

export default function useRegister() {
    const { isPaymentSuccess, name, email, password, confirm_password, credits, reset, hmac, setStatus, logoStorageKey } = useInstitutionRegistrationStore()
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

            const logo = await getImage(logoStorageKey)

            if (logo) {
                console.log("Logo sent");
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
                reset();
            }
        });

    }, [isPaymentSuccess, hmac, name, email, password, confirm_password, credits, logoStorageKey, reset, setStatus]);

    useEffect(() => {
        if (isPaymentSuccess) {
            handleRegistration();
        }
    }, [isPaymentSuccess, handleRegistration]);

    return isPending;
}