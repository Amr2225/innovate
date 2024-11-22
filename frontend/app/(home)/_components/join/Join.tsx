"use client";
import React from "react";
import Graphics from "./Graphics";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export default function Join() {
  const joinSteps = [
    "Purchase a plan that fits your active student count and your future needs",
    "Start adding your students and instructors into the system ",
    "Add your courses and prerequisites ans assign instructors",
    "That's it you have your own LMS",
  ];

  const listStyles = [
    "bg-blue-100 text-blue-400",
    "bg-secondary text-primary",
    "bg-secondary text-red-400/90",
    "bg-green-100 text-green-400",
  ];

  const variants = {
    show: {
      x: 0,
      opacity: 1,
      transition: { ease: "easeIn", duration: 0.8 },
    },
    hidden: {
      x: 30,
      opacity: 0,
    },
  };

  const container = {
    show: {
      y: 0,
      transition: { staggerChildren: 0.1, delayChildren: 0.3, duration: 1, delay: 0.5 },
      opacity: 1,
    },
    hidden: {
      y: 30,
      opacity: 0,
    },
  };

  return (
    <section className='bg-blue-50 min-h-[200px] py-8'>
      <h1 className='text-3xl font-bold text-center'>How to Join Us</h1>
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        whileInView={{ y: 0, opacity: 1, transition: { duration: 0.8 } }}
        viewport={{ once: true }}
        className='flex gap-2 justify-center items-center md:flex-row flex-col mt-12'
      >
        <motion.div
          variants={container}
          initial={"hidden"}
          whileInView={"show"}
          viewport={{ once: true }}
          className='px-2 [&_*]:overflow-hidden'
        >
          <h1 className='font-bold text-xl'>For Universities and Schools</h1>
          <ul className='space-y-5 mt-3 px-3 [&_p]:text-sm [&_p]:md:text-lg'>
            {joinSteps.map((step, index) => (
              <motion.li
                variants={variants}
                key={index}
                className='flex gap-2 items-center justify-start'
              >
                <span
                  className={cn(
                    "rounded-full size-10 aspect-square grid place-content-center font-bold text-xl w-max",
                    listStyles[index]
                  )}
                >
                  {index + 1}
                </span>
                <p>{step}</p>
              </motion.li>
            ))}
          </ul>
        </motion.div>
        <Graphics />
      </motion.div>
    </section>
  );
}
