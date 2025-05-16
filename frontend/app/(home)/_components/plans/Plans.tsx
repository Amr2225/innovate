"use client";
import React, { Suspense } from "react";
import { motion } from "framer-motion";
import { Skeleton } from "@/components/ui/skeleton";

export default function Plans({ children }: { children: React.ReactNode }) {
  const container = {
    show: {
      transition: { staggerChildren: 0.2, delayChildren: 0.4 },
    },
  };

  return (
    <section id='plans' className='-mt-10'>
      <motion.div
        variants={container}
        initial='hidden'
        whileInView='show'
        animate='show'
        viewport={{ once: true }}
        className='bg-white border shadow-md rounded-md md:p-10 p-2 md:!max-w-[70%] !max-w-[95%]'
      >
        <h1 className='text-3xl font-bold text-center mb-10'>Our Plans</h1>
        <Suspense fallback={<Skeleton className='w-full h-[500px]' />}>{children}</Suspense>
      </motion.div>
    </section>
  );
}
