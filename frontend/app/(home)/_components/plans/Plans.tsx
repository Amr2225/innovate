"use client";
import React from "react";
import PriceCards from "./PriceCards";
import { motion } from "framer-motion";

export default function Plans() {
  const container = {
    show: {
      transition: { staggerChildren: 0.2, delayChildren: 0.4 },
    },
  };

  return (
    <section className='-mt-10'>
      <motion.div
        variants={container}
        initial={"hidden"}
        whileInView={"show"}
        viewport={{ once: true }}
        className='bg-white border shadow-md rounded-md md:p-10 p-2 md:!max-w-[70%] !max-w-[95%]'
      >
        <h1 className='text-3xl font-bold text-center mb-10'>Our Plans</h1>
        <div className='flex flex-col md:flex-row gap-2 gap-y-8 items-center justify-between overflow-y-hidden'>
          <PriceCards type='silver' />
          <PriceCards type='gold' />
          <PriceCards type='diamond' />
        </div>
      </motion.div>
    </section>
  );
}
