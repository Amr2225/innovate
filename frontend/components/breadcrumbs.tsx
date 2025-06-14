"use client";
import React, { useEffect, useState } from "react";
import {
  Breadcrumb,
  // BreadcrumbLink,
  BreadcrumbSeparator,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb";
import { usePathname } from "next/navigation";
import { useBreadcrumb } from "@/context/breadcrumbsContext";
import Link from "next/link";

const roles = ["teacher", "institution", "student"];

const generateLink = (pathnames: string[], index: number): string => {
  const pathname = pathnames.slice(0, index + 1).join("/");
  return `/${pathname}`;
};

const renderCondition = (pathname: string) => {
  const pathnames = pathname.split("/").filter((path) => path);
  const lastPathname = pathnames[pathnames.length - 1];
  return roles.includes(lastPathname);
};

export function Breadcrumbs() {
  const { customPathnames, metadata } = useBreadcrumb();
  const pathname = usePathname();
  // Add client-side only rendering
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  // Skip rendering anything meaningful during SSR
  if (!isClient) {
    return (
      <Breadcrumb>
        <BreadcrumbList></BreadcrumbList>
      </Breadcrumb>
    );
  }

  const pathnames = customPathnames
    ? customPathnames.split("/").filter((path) => path)
    : pathname.split("/").filter((path) => path);

  return (
    <Breadcrumb>
      <BreadcrumbList>
        {pathnames.map((pathname, index) => (
          <React.Fragment key={index}>
            <BreadcrumbItem className='hidden md:block'>
              {index + 1 !== pathnames.length ? (
                renderCondition(pathname) ? (
                  <BreadcrumbPage className='text-neutral-500'>{pathname}</BreadcrumbPage>
                ) : (
                  <Link href={generateLink(pathnames, index)}>{pathname}</Link>
                )
              ) : (
                <BreadcrumbPage>
                  {metadata.has(pathname) ? metadata.get(pathname) : pathname}
                </BreadcrumbPage>
              )}
            </BreadcrumbItem>
            {pathnames.length !== index + 1 && <BreadcrumbSeparator className='hidden md:block' />}
          </React.Fragment>
        ))}
      </BreadcrumbList>
    </Breadcrumb>
  );
}
