import React from "react";
import Graphics from "./Graphics";

export default function Join() {
  return (
    <section className='bg-blue-50 min-h-[200px] py-8'>
      <h1 className='text-3xl font-bold text-center'>How to Join Us</h1>
      <div className='flex gap-2 justify-center items-center md:flex-row flex-col mt-12'>
        <div className=''>
          <h1 className='font-bold text-xl'>For Universities and Schools</h1>
          <ul className='space-y-5 mt-3 px-3 [&_p]:text-sm [&_p]:md:text-lg'>
            <li className='flex gap-2 items-center justify-start'>
              <span className='rounded-full bg-blue-100 text-blue-400 size-10 aspect-square grid place-content-center font-bold text-xl'>
                1
              </span>
              <p>Purchase a plan that fits your active student count and your future needs</p>
            </li>

            <li className='flex gap-2 items-center justify-start'>
              <span className='rounded-full bg-secondary text-primary size-10 aspect-square grid place-content-center font-bold text-xl'>
                2
              </span>
              <p>Purchase a plan that fits your active student count and your future needs</p>
            </li>

            <li className='flex gap-2 items-center justify-start'>
              <span className='rounded-full bg-secondary text-red-400/90 size-10 aspect-square grid place-content-center font-bold text-xl'>
                3
              </span>
              <p>Purchase a plan that fits your active student count and your future needs</p>
            </li>

            <li className='flex gap-2 items-center justify-start'>
              <span className='rounded-full bg-green-100 text-green-400 size-10 aspect-square grid place-content-center font-bold text-xl'>
                4
              </span>
              <p>Purchase a plan that fits your active student count and your future needs</p>
            </li>
          </ul>
        </div>
        <Graphics />
      </div>
    </section>
  );
}
