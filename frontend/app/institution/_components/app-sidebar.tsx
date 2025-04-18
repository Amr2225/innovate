"use client";
import {
  Home,
  Inbox,
  Search,
  Settings,
  UserRoundPlus,
  NotebookPen,
  ChevronRight,
} from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  // SidebarGroupAction,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar";
import Link from "next/link";
import UserProfile from "../../../components/user-profile";
import { redirect, usePathname } from "next/navigation";
import Image from "next/image";
import { Session } from "@/types/auth.type";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "../../../components/ui/collapsible";

// Menu items.
const items = [
  {
    title: "Home",
    url: "/dashboard",
    icon: Home,
  },
  {
    title: "Inbox",
    url: "/inbox",
    icon: Inbox,
  },
  {
    title: "Students",
    url: "/students",
    icon: UserRoundPlus,
  },
  {
    title: "Add Students",
    url: "/students/add",
    icon: UserRoundPlus,
  },
  {
    title: "Search",
    url: "/dashboard/search",
    icon: Search,
  },
  {
    title: "Settings",
    url: "/settings",
    icon: Settings,
  },
  {
    title: "Courses",
    url: "/courses",
    icon: NotebookPen,
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
          <SidebarGroupLabel>Teachers</SidebarGroupLabel>
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

        <SidebarGroup>
          <SidebarGroupLabel>Students</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <Link href={currentPath + item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>

                  <SidebarMenuSub>
                    <SidebarMenuSubItem>
                      <SidebarMenuButton>Button</SidebarMenuButton>
                    </SidebarMenuSubItem>
                  </SidebarMenuSub>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <Collapsible defaultOpen className='group/collapsible'>
          <SidebarGroup>
            <SidebarGroupLabel
              asChild
              className='group/label text-sm text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
            >
              <CollapsibleTrigger>
                Courses
                <ChevronRight className='ml-auto transition-transform group-data-[state=open]/collapsible:rotate-90' />
              </CollapsibleTrigger>
            </SidebarGroupLabel>

            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  {items.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton>
                        <item.icon />
                        <span>{item.title}</span>
                      </SidebarMenuButton>

                      {/* <SidebarMenuSub>
                        <SidebarMenuSubItem>
                          <SidebarMenuButton>Button</SidebarMenuButton>
                        </SidebarMenuSubItem>
                      </SidebarMenuSub> */}
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </SidebarGroup>
        </Collapsible>
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
