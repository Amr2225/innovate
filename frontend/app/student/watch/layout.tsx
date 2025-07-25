import React from "react";

// Components
import { Breadcrumbs } from "@/components/breadcrumbs";
import UserProfile from "@/components/user-profile";
import { redirect } from "next/navigation";

// Utils
import { getSession } from "@/lib/session";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { BreadcrumbProvider } from "@/context/breadcrumbsContext";
import CourseTitle from "./_components/courseTitle";

export default async function PreviewCourseLayout({ children }: { children: React.ReactNode }) {
  const session = await getSession();
  if (!session) redirect("/login");

  return (
    <BreadcrumbProvider>
      <main>
        <header className='flex sticky top-0 bg-background h-16 shrink-0 items-center gap-2 border-b px-4 z-50 justify-between'>
          <Breadcrumbs />
          <UserProfile
            email={session.user.email}
            name={session.user.name}
            role={session.user.role}
            profile_picture={session.user.profile_picture}
            className='ml-3'
            variant='icon'
          />
        </header>
        <div className='px-8 mt-2'>
          <Button variant='link' className='!pl-0' asChild>
            <Link href='/student/dashboard'>
              <ArrowLeft />
              Back to Course Page
            </Link>
          </Button>
          <CourseTitle />
          {children}
        </div>
      </main>
    </BreadcrumbProvider>
  );
}
