"use client";
import { Home, Settings, UserRoundPlus, NotebookPen, SquarePen } from "lucide-react";

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
import UserProfile from "../../../components/user-profile";
import { redirect, usePathname } from "next/navigation";
import Image from "next/image";
import { Session } from "@/types/auth.type";

// Menu items.
const items = [
  {
    title: "Dashboard",
    url: "/dashboard",
    icon: Home,
  },
  {
    title: "Students",
    url: "/students",
    icon: UserRoundPlus,
  },
  {
    title: "Courses",
    url: "/courses",
    icon: NotebookPen,
  },
  {
    title: "Assessments",
    url: "/assessments",
    icon: SquarePen,
  },
  {
    title: "Profile",
    url: "/profile",
    icon: Settings,
  },
];

export function AppSidebar({ session }: { session: Session }) {
  const currentPath = "/teacher";
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
              <div>
                <Image src='/logo.png' alt='logo' width={35} height={35} />
                <h1 className='text-2xl font-bold text-white'>Innovate</h1>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Home</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={pathname.endsWith(item.url)}>
                    <Link href={currentPath + item.url}>
                      <item.icon />
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
