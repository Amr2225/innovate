import React from "react";
import Image from "next/image";

import institutionImage from "../../../assets/institutions/institution.png";
import institutionImage2 from "../../../assets/institutions/institution2.png";
import institutionImage3 from "../../../assets/institutions/institution3.png";
import institutionImage4 from "../../../assets/institutions/institution4.png";
import institutionImage5 from "../../../assets/institutions/institution5.png";
import institutionImage6 from "../../../assets/institutions/institution6.png";
import institutionImage7 from "../../../assets/institutions/institution7.png";
import institutionImage8 from "../../../assets/institutions/institution8.png";

export default function Institutions() {
  const instituationImages = [
    institutionImage,
    institutionImage2,
    institutionImage3,
    institutionImage4,
    institutionImage5,
    institutionImage6,
    institutionImage7,
    institutionImage8,
  ];
  return (
    <section>
      <div className='flex justify-between items-start !w-[60%] gap-5'>
        <div className='w-[45%]'>
          <h1 className='font-bold text-3xl'>150 Trusted Institutions</h1>
          <p className='text-neutral-500'>
            Partnered with leading Institutions, we bring top-tier education to your fingertips. Our
            collaborative network ensures a diverse and enriching learning experience. Join us and
            excel with the best in academia.
          </p>
        </div>

        <div className='grid grid-cols-4 grid-rows-2 gap-y-3 gap-x-32 w-[55%]'>
          {instituationImages.map((image, index) => (
            <div
              className='size-[150px] aspect-square p-3 border shadow-sm rounded-md '
              key={index}
            >
              <Image src={image} alt='institution image' className='w-full h-full' />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
