import { Button } from "@/components/ui/button";
import React from "react";
import Graphics from "./Graphics";

export default function Hero() {
  return (
    <section className='bg-gradient-to-b from-transparent to-light w-full h-[90vh]'>
      <div className='flex gap-2 justify-center items-center md:flex-row flex-col-reverse'>
        <div className='space-y-3 text-center md:text-left md:w-[700px]'>
          <h1 className='capitalize text-4xl font-bold'>learn with expert anytime anywhere</h1>
          <h5 className='text-neutral-500 text-sm md:text-base'>
            Our mission is to innovate the learning journey for studnets with our intuitive and new
            assessment system and a user friendly interface.
            <span className='block mt-2 font-bold'>
              Your learning journey has never been easier
            </span>
          </h5>
          <Button className='w-[90%] font-bold text-lg capitalize' size={"lg"}>
            Login with access code
          </Button>
        </div>
        <Graphics />
      </div>
    </section>
  );
}
