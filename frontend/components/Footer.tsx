import Image from "next/image";
import Link from "next/link";
import React from "react";
import { Button } from "./ui/button";

export default function Footer() {
  return (
    <footer className='bg-blue-1000 py-10'>
      <div className='flex flex-col md:flex-row gap-5 justify-between md:items-center container px-3'>
        <div className=''>
          <div className='flex gap-2 items-start justify-start'>
            <Image src={"/Logo.png"} alt='Logo' width={40} height={40} />
            <h1 className='font-bold text-white text-3xl'>Innovate</h1>
          </div>
          <p className='text-neutral-500 font-bold mt-3'>Innovate, Educate, Elevate</p>
        </div>

        <div>
          <h5 className='uppercase text-white md:mb-5 mb-2'>quick links</h5>
          <ul className='md:space-y-3 [&>li]:text-neutral-400'>
            <li>
              <Button variant={"link"} asChild className='text-neutral-400 px-0'>
                <Link href={"/about"}>About Us</Link>
              </Button>
            </li>
            <li>
              <Button variant={"link"} asChild className='text-neutral-400 px-0'>
                <Link href={"/contact"}>Contact Us</Link>
              </Button>
            </li>
          </ul>
        </div>

        <div>
          <h5 className='uppercase text-white mb-2 md:mb-5'>Support</h5>
          <ul className='md:space-y-3 [&>li]:text-neutral-400'>
            <li>
              <Button variant={"link"} asChild className='text-neutral-400 px-0'>
                <Link href={"/faq"}>FAQs</Link>
              </Button>
            </li>
            <li>
              <Button variant={"link"} asChild className='text-neutral-400 px-0'>
                <Link href={"/terms-condition"}>Terms & Condition</Link>
              </Button>
            </li>
            <li>
              <Button variant={"link"} asChild className='text-neutral-400 px-0'>
                <Link href={"/privacy-policy"}>Privacy Policy</Link>
              </Button>
            </li>
          </ul>
        </div>
      </div>
    </footer>
  );
}
