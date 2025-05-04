import React from "react";

import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";

import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import { cn } from "@/lib/utils";
import UserProfile from "./user-profile";
import { getSession } from "@/lib/session";

// Used to deffirentiate between the authentication and nont-authentication pages
interface NavBarProps {
  isAuth?: boolean;
}

export default async function NavBar({ isAuth }: NavBarProps) {
  const session = await getSession();

  return (
    <nav className='p-6 px-2 md:px-14 flex items-center justify-between text-foreground border-b border-neutral-300'>
      <Link href={"/"} className='flex gap-2 items-center justify-start'>
        <Image src={"/Logo.png"} alt='Logo' width={40} height={40} />
        <h1 className='font-bold text-2xl md:text-3xl'>Innovate</h1>
      </Link>

      {/* On Small screens the nav will be in the footer only */}
      {!isAuth && (
        <>
          <NavigationMenu className='hidden md:block'>
            <NavigationMenuList>
              <NavigationMenuItem>
                <Link href='/about' legacyBehavior passHref>
                  <NavigationMenuLink className={cn(navigationMenuTriggerStyle())}>
                    About Us
                  </NavigationMenuLink>
                </Link>
              </NavigationMenuItem>

              <NavigationMenuItem>
                <Link href='/contact' legacyBehavior passHref>
                  <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                    Contact Us
                  </NavigationMenuLink>
                </Link>
              </NavigationMenuItem>

              <NavigationMenuItem>
                <Link href='/faq' legacyBehavior passHref>
                  <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                    FAQs
                  </NavigationMenuLink>
                </Link>
              </NavigationMenuItem>
            </NavigationMenuList>
          </NavigationMenu>

          {session ? (
            <div className='flex flex-col-reverse md:flex-row items-center justify-start gap-3 [&>*]:font-bold max-w-[200px] min-w-fit w-full'>
              <UserProfile
                name={session.user.name}
                email={session.user.email}
                role={session.user.role}
              />
            </div>
          ) : (
            <div className='flex flex-col-reverse md:flex-row items-center justify-start gap-3 [&>*]:font-bold max-w-[150px] min-w-fit'>
              <Button asChild className='w-full md:w-fit capitalize text-xs md:text-base'>
                <Link href={"/login"}>login</Link>
              </Button>

              <Button
                variant={"secondary"}
                className='capitalize w-full md:w-fit text-xs md:text-base'
                asChild
              >
                <Link href={"/login-access"}>login with access code</Link>
              </Button>
            </div>
          )}
        </>
      )}
    </nav>
  );
}
