"use client";
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { getCourseAvgScore } from "@/apiService/analytics";
import CountUp from "react-countup";
import { Loader2 } from "lucide-react";

export default function AvgCompletionRate() {
  const { data, isLoading } = useQuery({
    queryKey: ["course-avg-score"],
    queryFn: () => getCourseAvgScore(),
    select: (data) => data.overall_metrics.average_completion_rate,
  });

  if (isLoading) return <Loader2 className='size-10 mx-auto text-primary' />;

  return (
    <div className='flex flex-col items-center justify-center p-4 pb-0'>
      <div className='relative'>
        <div className='absolute inset-0 bg-gradient-to-br from-primary/10 to-primary/5 rounded-full blur-xl' />

        <div className='relative flex flex-col items-center'>
          <div className='flex items-baseline gap-2'>
            <p className='text-5xl font-bold bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent'>
              <CountUp end={data || 0} />%
            </p>
          </div>

          <div className='px-4 mt-0.5 py-1.5 bg-primary/5 rounded-full'>
            <p className='text-sm font-medium text-primary/80'>Avg Completion Rate</p>
          </div>
        </div>
      </div>
    </div>
  );
}
