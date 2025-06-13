"use client";
import {
  Home,
  Search,
  Settings,
  NotebookPen,
  BarChart4,
  Calendar,
  FileText,
  CreditCard,
  UserRoundPen,
  UsersRound,
} from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import Link from "next/link";
import UserProfile from "@/components/user-profile";
import { redirect, usePathname } from "next/navigation";
import Image from "next/image";
import { Session } from "@/types/auth.type";

// Home
const mainNavItems = [
  {
    title: "Dashboard",
    url: "/dashboard",
    icon: Home,
  },
  {
    title: "Analytics",
    url: "/analytics",
    icon: BarChart4,
  },
  {
    title: "Calendar",
    url: "/calendar",
    icon: Calendar,
  },
  {
    title: "Search",
    url: "/dashboard/search",
    icon: Search,
  },
];

// Users management items
const studentItems = [
  {
    title: "Users",
    url: "/users",
    icon: UsersRound,
  },
];

// Course management items
const courseItems = [
  {
    title: "Courses",
    url: "/courses",
    icon: NotebookPen,
  },
  {
    title: "Assessments",
    url: "/assessments",
    icon: FileText,
  },
];

// Settings and notifications
const utilityItems = [
  {
    title: "Billing",
    url: "/billing",
    icon: CreditCard,
  },
  {
    title: "Settings",
    url: "/settings",
    icon: Settings,
  },
  {
    title: "Profile",
    url: "/profile",
    icon: UserRoundPen,
  },
];

export function AppSidebar({ session }: { session: Session }) {
  const currentPath = "/institution";
  if (!session) redirect("/login");

  const pathname = usePathname();

  return (
    <Sidebar variant='floating' collapsible='icon' className='border-r-0 scrollbar'>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              className='data-[slot=sidebar-menu-button]:!p-1.5 hover:bg-transparent active:bg-transparent'
              variant='default'
              isActive={false}
            >
              <div className='flex items-center gap-2'>
                <Image src='/logo.png' alt='logo' width={35} height={35} />
                <h1 className='text-2xl font-bold text-white'>Innovate</h1>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        {/* Main Navigation */}
        <SidebarGroup>
          <SidebarGroupLabel>Home</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainNavItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={pathname.endsWith(item.url)}>
                    <Link href={currentPath + item.url}>
                      <item.icon className='h-5 w-5' />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Student Management */}
        <SidebarGroup>
          <SidebarGroupLabel>Users Management</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {studentItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={pathname.endsWith(item.url)}>
                    <Link href={currentPath + item.url}>
                      <item.icon className='h-5 w-5' />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Course Management */}
        <SidebarGroup>
          <SidebarGroupLabel>Course Management</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {courseItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={pathname.endsWith(item.url)}>
                    <Link href={currentPath + item.url}>
                      <item.icon className='h-5 w-5' />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Settings & Utilities */}
        <SidebarGroup>
          <SidebarGroupLabel>Settings</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {utilityItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={pathname.endsWith(item.url)}>
                    <Link href={currentPath + item.url}>
                      <item.icon className='h-5 w-5' />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <UserProfile
          name={session?.user.name}
          email={session?.user.email}
          role={session?.user.role}
        />
      </SidebarFooter>
    </Sidebar>
  );
}
