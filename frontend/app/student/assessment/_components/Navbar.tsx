import { Timer } from "lucide-react";
import moment from "moment";
import React, { useEffect, useState } from "react";

export function NavBar({
  assessmentTitle,
  courseName,
}: {
  assessmentTitle: string;
  courseName: string;
}) {
  const [time, setTime] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(time + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [time]);

  return (
    <header className='border-b shadow-md border-neutral-200 p-2 w-full'>
      <nav className='flex items-center justify-between w-full md:w-[85%] mx-auto'>
        <div>
          <h1 className='text-2xl font-bold'>{assessmentTitle}</h1>
          <p className='text-sm text-neutral-500'>{courseName}</p>
        </div>

        <div className='flex items-center gap-2'>
          <span className='bg-neutral-100 rounded-full p-2'>
            <Timer className='size-8 text-primary' />
          </span>
          <p className='text-lg font-semibold'>
            {moment().startOf("day").add(time, "seconds").format("HH:mm:ss")}
          </p>
        </div>
      </nav>
    </header>
  );
}
