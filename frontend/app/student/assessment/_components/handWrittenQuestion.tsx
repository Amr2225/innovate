"use client";
import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import QRCode from "react-qr-code";

import { Upload } from "lucide-react";
import Image from "next/image";
import { useParams } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { getHandwrittenImage, saveHandwrittenImage } from "@/store/handwrittenAnswerStorage";
import { createSolveAssessmentStore } from "@/store/solveAssessmentStore";

export default function HandWrittenQuestion({
  question,
  questionId,
}: {
  question: string;
  questionId: string;
}) {
  const { assessmentId } = useParams();
  console.log(questionId, assessmentId);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const ref = useRef<HTMLInputElement>(null);

  const { accessToken } = useAuth();
  const qrCodeUrl = `${process.env.NEXT_PUBLIC_SITE_URL}/assessment/upload?assessmentId=${assessmentId}&questionId=${questionId}&token=${accessToken}`;

  const useSolveAssessmentStore = createSolveAssessmentStore(assessmentId as string);
  const { handWrittenAnswers, setHandWrittenAnswer } = useSolveAssessmentStore();

  useEffect(() => {
    if (!accessToken) return;

    const event = new EventSource(
      `http://localhost:8000/assessment/sse/${accessToken}/${assessmentId}/${questionId}/`
    );
    event.onmessage = async (event) => {
      const data = JSON.parse(event.data);

      const imageDataUrl = `data:image/jpeg;base64,${data.image}`;

      try {
        await saveHandwrittenImage(questionId, imageDataUrl);
        console.log("Image saved successfully");
        setHandWrittenAnswer(`handwritten_${questionId}`, questionId);
      } catch (error) {
        console.error("Failed to save image:", error);
      }
    };

    return () => {
      event.close();
    };
  }, [accessToken, assessmentId, questionId, setHandWrittenAnswer]);

  // TODO: Make this a hook
  useEffect(() => {
    const getImageFromStorage = async () => {
      const image = await getHandwrittenImage(handWrittenAnswers[`handwritten_${questionId}`]);
      setUploadedImage(image);
    };
    getImageFromStorage();
  }, [handWrittenAnswers, questionId]);

  return (
    <div className='p-5 pt-2.5 mb-1'>
      <h1 className='text-lg font-semibold mb-2'>{question}</h1>
      <div className='pl-3'>
        <p>Scan the QR code and upload the photo from your phone or upload here directly</p>
        <p className='text-red-500 uppercase font-semibold'>
          Make Sure your handwritten is clear and is readable
        </p>
        {/* QR */}
        <div className='flex gap-5 items-start mt-5'>
          <QRCode size={175} value={qrCodeUrl} />

          {uploadedImage && (
            <div className='size-[200px] relative'>
              <Image src={uploadedImage} alt='Uploaded Image' layout='fill' objectFit='contain' />
            </div>
          )}
          <Input type='file' className='hidden' id='fileInput' ref={ref} />
          {!uploadedImage && (
            <Button variant='secondary' className='mt-2' onClick={() => ref.current?.click()}>
              Upload
              <Upload className='size-4' />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
