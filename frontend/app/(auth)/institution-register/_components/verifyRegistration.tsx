import { Card, CardContent } from "@/components/ui/card";
import { useInstitutionRegistrationStore } from "@/store/institutionRegistrationStore";
import { CheckCheck, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";

export function RegistrationVerification({
  isRegistrationSuccess,
  planId,
}: {
  isRegistrationSuccess: boolean | null;
  planId: string;
}) {
  const [timer, setTimer] = useState(5);
  const router = useRouter();

  useEffect(() => {
    const interval = setInterval(() => {
      setTimer(timer - 1);
    }, 1000);

    if (timer === 0) {
      useInstitutionRegistrationStore.getState().reset();

      if (isRegistrationSuccess) router.push("/institution/dashboard");
      else router.push(`/institution-register/${planId}`);
    }

    return () => clearInterval(interval);
  }, [timer, isRegistrationSuccess, router, planId]);

  return (
    <Card className='md:w-[500px] w-[350px] mx-auto'>
      <CardContent className='flex justify-center items-center'>
        <div>
          {isRegistrationSuccess ? (
            <div className='flex flex-col items-center justify-center p-5'>
              <span className='bg-green-600 rounded-full p-5'>
                <CheckCheck size={60} className='text-white' />
              </span>
              <h4 className='text-xl mt-3 text-center font-semibold capitalize'>
                Registration Successfully
              </h4>
              <p className='text-sm text-center text-gray-500'>
                Redirecting to your dashboard in {timer} seconds
              </p>
            </div>
          ) : (
            <div className='flex flex-col items-center justify-center p-5'>
              <span className='bg-red-600 rounded-full p-5'>
                <X size={60} className='text-white' />
              </span>
              <h4 className='text-xl mt-3 text-center font-semibold capitalize'>
                Registration Failed
              </h4>
              <p className='text-sm text-center text-gray-500'>
                Contact Customer Support If You need help {timer}
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
