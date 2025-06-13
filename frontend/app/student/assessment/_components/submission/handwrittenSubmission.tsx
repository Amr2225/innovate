import React, { useState } from "react";
import Image from "next/image";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ZoomIn } from "lucide-react";
import { HandwrittenQuestionSubmission } from "@/types/assessmentSubmission.type";

export default function HandwrittenSubmission({
  question_text,
  answer_image,
  feedback,
  extracted_text,
  score,
  max_score,
}: HandwrittenQuestionSubmission) {
  const [isImageOpen, setIsImageOpen] = useState(false);

  return (
    <div className='p-4 pt-2.5 mb-2'>
      <h3 className='font-semibold text-lg mb-2'>{question_text}</h3>

      <div className='flex h-full gap-5 items-start'>
        <div
          className='relative group h-[240px] w-[60%] rounded-lg overflow-hidden cursor-pointer border hover:shadow-lg transition-all duration-300'
          onClick={() => setIsImageOpen(true)}
        >
          <Image
            src={answer_image}
            alt='Uploaded Image'
            layout='fill'
            objectFit='cover'
            className='group-hover:scale-110 transition-all duration-500'
          />

          <div className='absolute inset-0 bg-neutral-800/60 opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-center justify-center'>
            <div className='text-white flex flex-col items-center gap-2 transform translate-y-4 group-hover:translate-y-0 transition-transform duration-300'>
              <ZoomIn className='h-8 w-8' />
              <span className='font-medium'>View Full Image</span>
            </div>
          </div>
        </div>

        <div>
          <div className='mb-4'>
            <p className='text-sm text-neutral-500 mb-1'>Score</p>
            <p className='font-semibold'>
              {Number(score).toFixed(1)}/{max_score}
            </p>
          </div>

          {extracted_text && (
            <div className='mb-4'>
              <p className='text-sm text-neutral-500 mb-1'>Extracted Text</p>
              <p className='p-2 bg-neutral-100 rounded-md text-sm'>{extracted_text}</p>
            </div>
          )}

          {feedback && (
            <div>
              <p className='text-sm text-neutral-500 mb-1'>Feedback</p>
              <p className='p-2 bg-neutral-100 rounded-md text-sm'>{feedback}</p>
            </div>
          )}
        </div>
      </div>

      {/* Image Dialog */}
      <Dialog open={isImageOpen} onOpenChange={setIsImageOpen}>
        <DialogContent className='max-w-4xl'>
          <DialogHeader>
            <DialogTitle>Handwritten Answer</DialogTitle>
          </DialogHeader>
          <div className='relative h-[80vh] w-full'>
            <Image
              src={answer_image}
              alt='Handwritten Answer'
              layout='fill'
              objectFit='contain'
              className='rounded-md'
            />
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
