import React from "react";
import PriceCards from "./PriceCards";

export default function Plans() {
  return (
    <section className='-mt-10'>
      <div className='bg-white border shadow-md rounded-md md:p-10 p-2 md:!max-w-[70%] !max-w-[95%]'>
        <h1 className='text-3xl font-bold text-center mb-10'>Our Plans</h1>
        <div className='flex gap-2 gap-y-8 items-center justify-between flex-wrap'>
          <PriceCards type='silver' />
          <PriceCards type='gold' />
          <PriceCards type='diamond' />
        </div>
      </div>
    </section>
  );
}
