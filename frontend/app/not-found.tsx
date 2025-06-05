import React from "react";
import Image from "next/image";
import notFoundImage from "../assets/not-found.png";

import NavBar from "@/components/navbar";
import BackButton from "@/components/backButton";

export default function Notfound() {
  return (
    <main>
      <NavBar />
      <div className='flex flex-col-reverse md:flex-row justify-center md:gap-32 items-center h-[90vh] container mx-auto'>
        <div className='grid place-content-center md:w-[500px] w-[300px]'>
          <h1 className='text-neutral-500 text-4xl font-bold'>Error 404</h1>
          <h2 className='font-bold text-2xl mb-3'>Oops! page not found</h2>
          <p className='my-5'>
            Something went wrong. It&apos;s look that your requested could not be found. It&apos;s
            look like the link is broken or the page is removed.
          </p>
          <BackButton />
        </div>
        <Image src={notFoundImage} alt='Not Found Image' width={500} height={500} />
      </div>
    </main>
  );
}
