import React from "react";
import Hero from "./_components/hero/Hero";
import Learning from "./_components/start_learning/Learning";
import Join from "./_components/join/Join";
import Plans from "./_components/plans/Plans";
import AssessmentSystemIntro from "./_components/assessment/page";
import Testimonial from "./_components/testimonial/page";
import Institutions from "./_components/institutions/Institutions";
import PriceCardsWrapper from "./_components/plans/PriceCardsWrapper";

export default function HomePage() {
  return (
    <div>
      <div className='[&>section>*]:container [&>section>*]:mx-auto'>
        <Hero />
        <hr className='my-5 border-none ' />
        <Learning />
        <hr className='my-5 border-none ' />
        <Join />
        <Plans>
          <PriceCardsWrapper />
        </Plans>
        <hr className='my-5 border-none ' />
        <AssessmentSystemIntro />
        <hr className='my-5 border-none ' />
        <Testimonial />
        <hr className='my-5 border-none ' />
        <Institutions />
      </div>
    </div>
  );
}
