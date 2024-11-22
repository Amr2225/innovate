"use client";
import React from "react";
import Graphics from "./Graphics";
import { motion } from "framer-motion";

export default function Learning() {
  const learningSteps = [
    "Login to your institution with your access code",
    "Create your account for the first time",
    "Start innovating your learning!",
  ];

  return (
    <section>
      <motion.div
        className='flex gap-2 justify-center items-center md:flex-row flex-col-reverse'
        initial={{ y: 100, opacity: 0 }}
        whileInView={{
          y: 0,
          opacity: 1,
          transition: { duration: 1, delay: 0.1, ease: [0.32, 0.23, 0.4, 0.9] },
        }}
        viewport={{ once: true }}
      >
        <Graphics />
        <div>
          <h1 className='capitalize text-2xl font-bold text-center md:text-left'>
            how to start learning?
          </h1>
          <ul className='space-y-5 mt-3 px-3 [&_p]:text-sm [&_p]:md:text-lg'>
            {learningSteps.map((step, index) => (
              <li key={index} className='flex gap-2 items-center justify-start'>
                <span className='rounded-full bg-secondary text-primary size-10 aspect-square grid place-content-center font-bold text-xl w-max'>
                  {index + 1}
                </span>
                <p>{step}</p>
              </li>
            ))}
          </ul>
        </div>
      </motion.div>
    </section>
  );
}
