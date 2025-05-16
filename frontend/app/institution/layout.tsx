import { Breadcrumbs } from "@/components/breadcrumbs";
import { AppSidebar } from "./_components/app-sidebar";

import { Separator } from "@/components/ui/separator";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import UserProfile from "@/components/user-profile";
import { getSession } from "@/lib/session";
import { redirect } from "next/navigation";
import React from "react";

export default async function InstitutionDashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getSession();
  if (!session) redirect("/login");

  return (
    <SidebarProvider>
      <AppSidebar session={session} />
      <SidebarInset>
        <header className='flex sticky top-0 bg-background h-16 shrink-0 items-center gap-2 border-b px-4'>
          <SidebarTrigger className='-ml-1' />
          <Separator orientation='vertical' className='mr-2 h-4' />
          <Breadcrumbs />
          <div className='flex flex-col items-start justify-center ml-auto'>
            <h1 className='text-sm font-bold'>Credits</h1>
            <p className='text-sm text-muted-foreground'>{session.user.credits}</p>
          </div>
          <UserProfile
            email={session.user.email}
            name={session.user.name}
            role={session.user.role}
            profile_picture={session.user.profile_picture}
            className='ml-3'
            variant='icon'
          />
        </header>
        <div className='bg-primary-background h-full'>
          <div className='container bg-white mx-auto h-[85%] mt-12 py-2 px-4'>{children}</div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
