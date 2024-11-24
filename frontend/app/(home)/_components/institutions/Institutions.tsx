import React from "react";
import Image from "next/image";

import institutionImage from "../../../../assets/institutions/institution.png";
import institutionImage2 from "../../../../assets/institutions/institution2.png";
import institutionImage3 from "../../../../assets/institutions/institution3.png";
import institutionImage4 from "../../../../assets/institutions/institution4.png";
import institutionImage5 from "../../../../assets/institutions/institution5.png";
import institutionImage6 from "../../../../assets/institutions/institution6.png";
import institutionImage7 from "../../../../assets/institutions/institution7.png";
import institutionImage8 from "../../../../assets/institutions/institution8.png";

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
      <div className='flex flex-col md:flex-row justify-between items-start md:!w-[60%] gap-5 px-3'>
        <div className='md:w-[45%]'>
          <h1 className='font-bold text-3xl'>150 Trusted Institutions</h1>
          <p className='text-neutral-500'>
            Partnered with leading Institutions, we bring top-tier education to your fingertips. Our
            collaborative network ensures a diverse and enriching learning experience. Join us and
            excel with the best in academia.
          </p>
        </div>

        <div className='grid md:grid-cols-4 md:grid-rows-2 grid-cols-3 grid-rows-3 md:gap-x-32 gap-4 mx-auto md:w-[55%]'>
          {instituationImages.map((image, index) => (
            <div
              className='md:size-[150px] size-[100px] aspect-square p-3 border shadow-sm rounded-md '
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
