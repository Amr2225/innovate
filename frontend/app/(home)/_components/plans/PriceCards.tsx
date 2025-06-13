"use client";
import React from "react";

import { Button } from "@/components/ui/button";
import { X, Check } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";

import { motion } from "framer-motion";
import { Plan } from "@/types/institution.type";

function getTitle(studentLimit: number) {
  return `1 Credit = ${studentLimit} Students`;
}

function getDescription(text: string, isAdvantage: boolean, key: number) {
  return (
    <li className='flex gap-3' key={key}>
      {isAdvantage ? <Check className='text-green-500' /> : <X className='text-red-500' />}
      <p className='capitalize'>{text}</p>
    </li>
  );
}

const variant = {
  show: {
    y: 0,
    opacity: 1,
    transition: { duraiton: 0.8, ease: "easeInOut" },
  },
  hidden: {
    y: 20,
    opacity: 0,
  },
};

export default function PriceCards({
  id,
  type,
  description,
  currency,
  students_limit,
  credit_price,
}: Plan) {
  return (
    <motion.div variants={variant} className='border shadow-lg rounded-lg w-full'>
      <header className='bg-gradient-to-r from-primary-dark to-primary flex justify-between items-center px-4 h-14 rounded-se-md rounded-ss-md'>
        <h1 className='font-bold text-lg text-white'>{getTitle(students_limit)}</h1>
        <Badge className='py-1' variant={type}>
          {type}
        </Badge>
      </header>
      <div className='p-5'>
        <h1 className='text-2xl mt-5 font-bold'>
          Credit Price {credit_price} {currency}
        </h1>
        <Button
          variant={"secondary"}
          className='w-full my-6 rounded-full hover:bg-primary hover:text-primary-foreground transition-all'
        >
          <Link href={`/institution-register/${id}`}>Buy Now</Link>
        </Button>
        <ul className='space-y-4'>
          {description.map((data, index) => getDescription(data.text, data.isAdvantage, index))}
        </ul>
      </div>
    </motion.div>
  );
}
