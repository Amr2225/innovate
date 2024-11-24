import { Button } from "@/components/ui/button";
import Link from "next/link";
import React from "react";

export default function Testimonial() {
  return (
    <section className='bg-blue-1000 py-10'>
      <div className='flex flex-col md:flex-row items-center justify-between md:!w-[60%] px-3 md:px-0 gap-8'>
        <div className=''>
          <h1 className='text-3xl text-white md:w-[80%] font-bold mb-4'>
            Start learning with 67.1K students around the world
          </h1>

          <div className='space-x-3'>
            <Button asChild>
              <Link href={"/login-access"}>Join the Family</Link>
            </Button>
            <Button variant={"outline"}>
              <Link href={"/login"}>Login</Link>
            </Button>
          </div>
        </div>

        <div className='flex justify-between items-center [&_h3]:text-white [&_h3]:text-2xl md:w-[55%] w-full'>
          <div>
            <h3 className='font-bold'>150</h3>
            <p className='text-neutral-500 font-bold text-sm md:text-base'>Institution</p>
          </div>

          <div>
            <h3 className='font-bold'>26K</h3>
            <p className='text-neutral-500 font-bold text-sm md:text-base'>Certified Instructor</p>
          </div>

          <div>
            <h3 className='font-bold'>99.9%</h3>
            <p className='text-neutral-500 font-bold text-sm md:text-base'>Success Rate</p>
          </div>
        </div>
      </div>
    </section>
  );
}
