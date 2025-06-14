import React, { use } from "react";

// Components
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";

// Libs
import { getSession, logout } from "@/lib/session";
import { getNameInitials } from "@/lib/getNameInitials";

// Components
import StudentTabs from "./_components/studentTabs";

export default function StudentDashboard() {
  const session = use(getSession());
  if (!session) {
    logout();
    return;
  }

  const nameInitial = getNameInitials(session.user.name);

  return (
    <div className='w-full max-h-full'>
      <div className='bg-primary/20 h-[150px] w-full' />

      <div className='w-[80%] h-[650px] -mt-20 bg-white rounded-md shadow-m mx-auto'>
        <header className='py-5 mx-auto flex items-center justify-center gap-4'>
          <Avatar className='h-16 w-16 rounded-full'>
            <AvatarImage src='https://github.com/shadcn.png' alt={"user-profile"} />
            <AvatarFallback className='rounded-lg bg-primary text-white items-center justify-center flex'>
              {nameInitial}
            </AvatarFallback>
          </Avatar>

          <div className='flex flex-col'>
            <h1 className='text-2xl font-bold capitalize'>{session.user.name}</h1>
            {/* <p className='text-gray-500'>Student Level / GPA</p> */}
            <p className='text-gray-500'>{session.user.email}</p>
          </div>
        </header>
        <Separator />
        <StudentTabs name={session.user.name.split(" ")[0]} />
      </div>
    </div>
  );
}
