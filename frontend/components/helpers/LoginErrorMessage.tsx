import { TriangleAlert } from "lucide-react";
import React from "react";
import { Button } from "../ui/button";
import Link from "next/link";
import { LoginError } from "@/types/auth.type";
import { redirect } from "next/navigation";

interface LoginErrorProps {
  error: LoginError | null;
}

export default function LoginErrorMessage({ error }: LoginErrorProps) {
  if (!error?.message) return null;

  return (
    <div className='bg-destructive/15 p-3 rounded-md flex items-center gap-x-2 text-sm text-destructive'>
      <TriangleAlert className='size-4' />
      <div className='flex justify-between items-center w-full'>
        <p>{error.message}</p>
        {error.type === "Verification" && (
          <Link href={"/verify-email"}>
            <Button
              type='button'
              variant={"link"}
              className='text-black'
              onClick={() => redirect("/verify-email")}
            >
              Resend Verification
            </Button>
          </Link>
        )}
      </div>
    </div>
  );
}
