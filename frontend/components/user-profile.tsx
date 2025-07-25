"use client";
import React from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  ChevronsUpDown,
  CreditCard,
  LogOut,
  LayoutDashboard,
  Settings,
  UserRoundPen,
} from "lucide-react";
import { logout } from "@/lib/session";
import { redirect } from "next/navigation";
import { cn } from "@/lib/utils";
import { User } from "@/types/user.types";
import Link from "next/link";
import { getNameInitials } from "@/lib/getNameInitials";

interface UserProfileProps extends User {
  variant?: "default" | "icon";
  className?: string;
}

const handleLogout = async () => {
  await logout();
  redirect("/");
};

export default function UserProfile({
  name,
  email,
  role,
  profile_picture,
  variant = "default",
  className,
}: UserProfileProps) {
  const nameInitial = React.useMemo(() => getNameInitials(name), [name]);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        className={cn(
          "flex flex-row gap-3 items-center justify-start focus-visible:outline-none",
          className
        )}
      >
        <>
          <Avatar className='h-8 w-8 rounded-lg'>
            <AvatarImage src={profile_picture} alt={"user-profile"} />
            <AvatarFallback className='rounded-lg bg-primary text-white items-center justify-center flex'>
              {nameInitial}
            </AvatarFallback>
          </Avatar>
          {variant === "default" && (
            <>
              <div className='grid flex-1 text-left text-sm leading-tight'>
                <span className='truncate font-semibold'>{name}</span>
                <span className='truncate text-xs'>{email}</span>
              </div>
              <ChevronsUpDown className='ml-auto size-4' />
            </>
          )}
        </>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        className='w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg'
        // side={isMobile ? "bottom" : "right"}
        side='bottom'
        align='end'
        sideOffset={4}
      >
        <DropdownMenuLabel className='p-0 font-normal'>
          <div className='flex items-center gap-2 px-1 py-1.5 text-left text-sm'>
            <Avatar className='h-8 w-8 rounded-lg'>
              <AvatarImage src={profile_picture} alt={"user-profile"} />
              <AvatarFallback className='rounded-lg'>CN</AvatarFallback>
            </Avatar>
            <div className='grid flex-1 text-left text-sm leading-tight'>
              <span className='truncate font-semibold'>{name}</span>
              <span className='truncate text-xs'>{email}</span>
            </div>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />

        <DropdownMenuGroup>
          <DropdownMenuItem asChild>
            <Link
              href={`/${role.toLowerCase()}/dashboard`}
              className='flex items-center text-black'
            >
              <LayoutDashboard />
              Dashboard
            </Link>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
        </DropdownMenuGroup>

        <DropdownMenuGroup>
          {role === "Institution" && (
            <>
              <DropdownMenuItem asChild>
                <Link href='/institution/billing'>
                  <CreditCard />
                  Billing
                </Link>
              </DropdownMenuItem>

              <DropdownMenuItem asChild>
                <Link href='/institution/settings'>
                  <Settings />
                  Settings
                </Link>
              </DropdownMenuItem>
            </>
          )}

          <DropdownMenuItem asChild>
            <Link href='/institution/profile'>
              <UserRoundPen />
              Profile
            </Link>
          </DropdownMenuItem>
        </DropdownMenuGroup>

        <DropdownMenuSeparator />
        <DropdownMenuItem className='cursor-pointer' onClick={handleLogout}>
          <LogOut />
          Log out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
