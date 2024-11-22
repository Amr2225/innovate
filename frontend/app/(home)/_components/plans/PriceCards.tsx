import React from "react";

import { Button } from "@/components/ui/button";
import { X, Check } from "lucide-react";
import Link from "next/link";

interface PriceCardsProps {
  type: PricePlans;
}

type PricePlans = "silver" | "gold" | "diamond";

function getTitle(type: PricePlans) {
  switch (type) {
    case "silver":
      return "1 To 1";
    case "gold":
      return "1 To 5";
    case "diamond":
      return "1 To 10";
  }
}

function getDescription(type: PricePlans) {
  switch (type) {
    case "silver":
      return (
        <>
          <li className='flex gap-3'>
            <Check className='text-green-500' />
            <p>Best suited for small institutions</p>
          </li>
          <li className='flex gap-3'>
            <Check className='text-green-500' />
            <p>No minimum student amount needed</p>
          </li>
          <li className='flex gap-3'>
            <X className='text-red-500' />
            <p>No offers will be granted</p>
          </li>
        </>
      );
    case "gold":
      return (
        <>
          <li className='flex gap-3'>
            <Check className='text-green-500' />
            <p>Best suited for medium institutions</p>
          </li>
          <li className='flex gap-3'>
            <Check className='text-green-500' />
            <p>Minimum amount is 1,000 student</p>
          </li>
          <li className='flex gap-3'>
            <Check className='text-red-500' />
            <p>Offers will be granted yearly</p>
          </li>
        </>
      );
    case "diamond":
      return (
        <>
          <li className='flex gap-3'>
            <Check className='text-green-500' />
            <p>Best suited for large institutions</p>
          </li>
          <li className='flex gap-3'>
            <Check className='text-green-500' />
            <p>Minimum amount is 10,000 students</p>
          </li>
          <li className='flex gap-3'>
            <Check className='text-red-500' />
            <p>Offers will be granted monthly</p>
          </li>
        </>
      );
  }
}

export default function PriceCards({ type }: PriceCardsProps) {
  return (
    <div className='border shadow-lg rounded-lg md:hover:-translate-y-2 transition-transform w-full md:w-fit'>
      <header className='bg-gradient-to-r from-primary-dark to-primary flex justify-between items-center px-8 h-14 rounded-se-md rounded-ss-md'>
        <h1 className='font-bold text-xl text-white'>{getTitle(type)}</h1>
      </header>
      <div className='p-5'>
        <h1 className='md:text-2xl  mt-5 font-bold'>
          {getTitle(type).replace("To", "Credit = ") + " Students"}
        </h1>
        <Button
          variant={"secondary"}
          className='w-full my-6 rounded-full hover:bg-primary hover:text-primary-foreground transition-all'
        >
          <Link href={"/buy"}>Buy Now</Link>
        </Button>
        <ul className='space-y-4'>{getDescription(type)}</ul>
      </div>
    </div>
  );
}
