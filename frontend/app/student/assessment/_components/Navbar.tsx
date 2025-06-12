import { Timer } from "lucide-react";
import moment from "moment";
import React, { useEffect, useState } from "react";

interface NavBarProps {
  assessmentTitle: string;
  courseName: string;
  startTime?: Date;
  endTime?: Date;
  totalScore?: number;
  score?: number;
}

export function NavBar({
  assessmentTitle,
  courseName,
  startTime,
  endTime,
  totalScore,
  score,
}: NavBarProps) {
  const [timeLeft, setTimeLeft] = useState(0);

  useEffect(() => {
    if (!endTime) return;
    const interval = setInterval(() => {
      setTimeLeft(moment(endTime).diff(moment(startTime), "milliseconds"));
    }, 1000);

    return () => clearInterval(interval);
  }, [endTime, startTime]);

  const formatTimeLeft = () => {
    const duration = moment.duration(timeLeft);
    const days = Math.floor(duration.asDays());
    const hours = duration.hours();
    const minutes = duration.minutes();
    const seconds = duration.seconds();

    if (days > 0) {
      return `${days} Days ${hours.toString().padStart(2, "0")}:${minutes
        .toString()
        .padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
    } else {
      return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds
        .toString()
        .padStart(2, "0")}`;
    }
  };

  return (
    <header className='border-b shadow-md border-neutral-200 p-2 w-full'>
      <nav className='flex items-center justify-between w-full md:w-[85%] mx-auto'>
        <div>
          <h1 className='text-2xl font-bold'>{assessmentTitle}</h1>
          <p className='text-sm text-neutral-500'>{courseName}</p>
        </div>

        {endTime && (
          <div className='flex items-center gap-2'>
            <span className='bg-neutral-100 rounded-full p-2'>
              <Timer className='size-8 text-primary' />
            </span>
            <p className='text-lg font-semibold'>{formatTimeLeft()}</p>
          </div>
        )}
        {totalScore && score && (
          <div>
            <h4 className='text-primary text-sm font-semibold'>Total Score</h4>
            <p className='flex items-center gap-2'>
              <span className=''>{score.toFixed(1)}</span>
              <span>/</span>
              <span className='font-semibold'>{totalScore}</span>
            </p>
          </div>
        )}
      </nav>
    </header>
  );
}
