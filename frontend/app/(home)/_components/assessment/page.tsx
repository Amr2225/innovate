import React from "react";

import { HandwrittenGraphics, MCQGrahpics } from "./Graphics";

export default function AssessmentSystem() {
  return (
    <section>
      <h1 className='text-3xl font-bold text-center'>Our Innovated Assessment System</h1>
      <div className='md:!w-[60%] px-3'>
        {/*  */}
        <div className='flex flex-col-reverse md:flex-row gap-3 items-center justify-center '>
          <div className='w-full'>
            <h1 className='text-xl font-bold my-3'>Handwritten Exams</h1>
            <p className='text-neutral-500'>
              Our cutting-edge handwritten system revolutionizes exam-taking by offering a unique
              handwritten exam format. Each exam is seamlessly evaluated by our advanced AI,
              ensuring accuracy and efficiency. Experience the future of assessments with our
              innovative technology. Join us in transforming the way you learn and succeed. Your
              academic journey just got smarter and more intuitive. Embrace the change with our
              state-of-the-art system.
            </p>
          </div>
          <div className='w-[350px] aspect-square'>
            <HandwrittenGraphics />
          </div>
        </div>

        {/* <div className='flex flex-col md:flex-row gap-3 items-center justify-center '>
          <div className='size-[350px] aspect-square'>
            <CodingGraphics />
          </div>
          <div className='w-full'>
            <h1 className='text-xl font-bold my-3'>Coding Exams</h1>
            <p className='text-neutral-500'>
              Our state-of-the-art coding exam system redefines how you test your programming
              skills. Each exam is meticulously evaluated by our advanced AI, ensuring precision and
              fairness. Dive into the future of coding assessments with our innovative technology.
              Join us in transforming the way you learn and succeed in the tech world. Your coding
              journey just got smarter and more intuitive.
            </p>
          </div>
        </div> */}

        <div className='flex flex-col-reverse md:flex-row gap-3 items-center justify-center '>
          <div className='w-[350px] aspect-square'>
            <MCQGrahpics />
          </div>
          <div className='w-full'>
            <h1 className='text-xl font-bold my-3'>MCQ Exams</h1>
            <p className='text-neutral-500'>
              Our innovative system offers a dynamic MCQ exam format, tailored uniquely for each
              student. Leveraging advanced AI, we generate personalized multiple-choice questions to
              enhance learning and assessment. Experience the future of education with our
              cutting-edge technology. Join us in revolutionizing the way you learn and succeed.
              Your academic journey just became more engaging and effective.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
