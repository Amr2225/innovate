import React from "react";
import Graphics from "./Graphics";

export default function Learning() {
  return (
    <section>
      <div className='flex gap-2 justify-center items-center md:flex-row flex-col-reverse'>
        <Graphics />
        <div className=''>
          <h1 className='capitalize text-2xl font-bold text-center md:text-left'>
            how to start learning?
          </h1>
          <ul className='space-y-5 mt-3 px-3 [&_p]:text-sm [&_p]:md:text-lg'>
            <li className='flex gap-2 items-center justify-start'>
              <span className='rounded-full bg-secondary text-primary size-10 aspect-square grid place-content-center font-bold text-xl w-max'>
                1
              </span>
              <p>Login to your institution with your access code</p>
            </li>

            <li className='flex gap-2 items-center justify-start'>
              <span className='rounded-full bg-secondary text-primary size-10 aspect-square grid place-content-center font-bold text-xl w-max'>
                2
              </span>
              <p>Create your account for the first time</p>
            </li>

            <li className='flex gap-2 items-center justify-start'>
              <span className='rounded-full bg-secondary text-primary size-10 aspect-square grid place-content-center font-bold text-xl w-max'>
                3
              </span>
              <p>Start innovating your learning!</p>
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
}
