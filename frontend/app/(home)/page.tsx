import React from "react";
import Hero from "./_components/hero/Hero";
import Learning from "./_components/start_learning/Learning";
import Join from "./_components/join/Join";

export default function HomePage() {
  return (
    <div>
      <div className='[&>section>*]:container [&>section>*]:mx-auto'>
        <Hero />
        <hr className='my-5 border-none ' />
        <Learning />
        <hr className='my-5 border-none ' />
        <Join />
      </div>
    </div>
  );
}
