"use client";
import { Button } from "@/components/ui/button";
import { CheckCircle2 } from "lucide-react";
import confetti from "canvas-confetti";
import { useEffect } from "react";
import Link from "next/link";

export default function SubmissionSuccessPage() {
  useEffect(() => {
    // Trigger confetti effect when page loads
    const duration = 3 * 1000;
    const end = Date.now() + duration;

    const runConfetti = () => {
      confetti({
        particleCount: 3,
        angle: 60,
        spread: 55,
        origin: { x: 0 },
        colors: ["#4F46E5", "#10B981", "#6366F1"],
      });

      confetti({
        particleCount: 3,
        angle: 120,
        spread: 55,
        origin: { x: 1 },
        colors: ["#4F46E5", "#10B981", "#6366F1"],
      });

      if (Date.now() < end) {
        requestAnimationFrame(runConfetti);
      }
    };

    runConfetti();
  }, []);

  return (
    <div className='min-h-screen bg-gradient-to-b from-white to-neutral-50 flex items-center justify-center px-4'>
      <div className='max-w-md w-full bg-white rounded-xl shadow-lg p-8 animate-fade-in-up'>
        <div className='flex flex-col items-center text-center'>
          <div className='h-24 w-24 rounded-full bg-green-50 flex items-center justify-center mb-6'>
            <CheckCircle2 className='h-16 w-16 text-green-500' />
          </div>

          <h1 className='text-2xl font-bold text-gray-900 mb-2'>Submission Successful!</h1>

          <p className='text-neutral-600 mb-8'>
            Your assessment has been submitted successfully. Your instructor will review it and
            provide feedback soon.
          </p>

          <Button
            className='w-full py-6 text-base font-medium transition-all hover:scale-105'
            asChild
          >
            <Link href='/student/dashboard'>Go Back to Dashboard</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
