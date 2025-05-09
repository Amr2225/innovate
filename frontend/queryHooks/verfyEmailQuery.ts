import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';

import { VerifyEmailQueryProps } from '@/components/verifyEmailCard';


export default function useVerifyEmailQuery({ emailToken,
    verifyEmail,
    verifyEmailExists,
    resendVerificationEmail,
    sucessRedirectionURL,
    failureRedirectionURL,
    successCallback,
    failureCallback,
}: VerifyEmailQueryProps) {
    const router = useRouter();
    const { isError, isLoading } = useQuery({
        queryKey: ["verifyEmailToken"],
        queryFn: () => verifyEmailExists(emailToken),
        retry: 15,
        staleTime: 1000 * 60 * 15,
    });

    const { mutate: verifyEmailMutation, isPending } = useMutation({
        mutationFn: (otp: number) => verifyEmail(otp, emailToken),
        onSuccess: () => {
            router.push(sucessRedirectionURL);
            toast.success("Email verified successfully");
            successCallback?.();
        },
        onError: (e) => {
            toast.error(e.message);
        },
    });

    const { mutate: resendEmailMutation } = useMutation({
        mutationFn: () => resendVerificationEmail(emailToken),
        onSuccess: () => {
            toast.success("Verification email sent");
        },
        onError: (e) => {
            toast.error(e.message);
        },
    });


    useEffect(() => {
        if (isError) {
            router.push(failureRedirectionURL);
            toast.error("Resend the verification OTP");
            failureCallback?.();
        }
    }, [isError, router, failureRedirectionURL, failureCallback]);

    return { verifyEmailMutation, isPending, isLoading, resendEmailMutation };
}
