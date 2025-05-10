"use client";
import React from "react";
import {
  Breadcrumb,
  BreadcrumbLink,
  BreadcrumbSeparator,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb";
import { usePathname } from "next/navigation";

const generateLink = (pathnames: string[], index: number): string => {
  const pathname = pathnames.slice(0, index + 1).join("/");
  return `/${pathname}`;
};

export function Breadcrumbs() {
  const pathname = usePathname();
  const pathnames = pathname.split("/").filter((name) => name);

  return (
    <Breadcrumb>
      <BreadcrumbList>
        {pathnames.map((pathname, index) => (
          <React.Fragment key={index}>
            <BreadcrumbItem className='hidden md:block'>
              {index + 1 !== pathnames.length ? (
                <BreadcrumbLink href={generateLink(pathnames, index)}>{pathname}</BreadcrumbLink>
              ) : (
                <BreadcrumbPage>{pathname}</BreadcrumbPage>
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
