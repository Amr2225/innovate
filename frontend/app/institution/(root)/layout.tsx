import { Breadcrumbs } from "@/components/breadcrumbs";
import { AppSidebar } from "./_components/app-sidebar";

import { Separator } from "@/components/ui/separator";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import UserProfile from "@/components/user-profile";
import { getSession } from "@/lib/session";
import { redirect } from "next/navigation";
import React from "react";
import { BreadcrumbProvider } from "@/context/breadcrumbsContext";

export default async function InstitutionDashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getSession();
  if (!session) redirect("/login");

  return (
    <SidebarProvider>
      <BreadcrumbProvider>
        <AppSidebar session={session} />
        <SidebarInset className='hide-scrollbar'>
          <header className='flex sticky top-0 bg-background h-16 shrink-0 items-center gap-2 border-b px-4 z-50'>
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
          <div className='bg-primary-background max-h-full overflow-hidden'>
            <div className='container bg-white mx-auto h-full hide-scrollbar overflow-hidden mt-12 py-2 px-4 w-full'>
              {children}
            </div>
          </div>
        </SidebarInset>
      </BreadcrumbProvider>
    </SidebarProvider>
  );
}
