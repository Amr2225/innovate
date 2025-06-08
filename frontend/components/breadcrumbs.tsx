"use client";
import React from "react";
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

const generateLink = (pathnames: string[], index: number): string => {
  const pathname = pathnames.slice(0, index + 1).join("/");
  return `/${pathname}`;
};

export function Breadcrumbs() {
  const { customPathnames, metadata } = useBreadcrumb();
  const pathname = usePathname();
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
                <Link href={generateLink(pathnames, index)}>{pathname}</Link>
              ) : (
                <BreadcrumbPage>
                  {metadata.has(pathname) ? metadata.get(pathname) : pathname}
                </BreadcrumbPage>
              )}
            </BreadcrumbItem>
            {pathnames.length !== index + 1 && <BreadcrumbSeparator className='hidden md:block' />}
            {/* <BreadcrumbItem>
              <BreadcrumbPage>Data Fetching</BreadcrumbPage>
            </BreadcrumbItem> */}
          </React.Fragment>
        ))}
      </BreadcrumbList>
    </Breadcrumb>
  );
}
