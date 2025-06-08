import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import QRCode from "react-qr-code";
import { io } from "socket.io-client";

import { Upload } from "lucide-react";
import Image from "next/image";
import { useParams } from "next/navigation";

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
  const qrCodeUrl = `${process.env.NEXT_PUBLIC_SITE_URL}/student/assessment/upload?assessmentId=${assessmentId}&questionId=${questionId}`;

  useEffect(() => {
    // Initialize socket connection
    const socket = io({
      path: "/api/socket",
    });

    // Join the specific assessment room
    socket.emit("joinAssessment", assessmentId);

    // Listen for new images
    socket.on("newImage", (data) => {
      // Only update if the image is for this question
      if (data.questionId === questionId) {
        console.log(data);
        setUploadedImage(data.image);

        // Optionally store in IndexedDB for offline access
        // storeImageInIndexedDB(assessmentId, questionId, data.image);
      }
    });

    // Check IndexedDB for cached image on load
    // loadImageFromIndexedDB(assessmentId, questionId).then(image => {
    //   if (image) {
    //     setUploadedImage(image);
    //   }
    // });

    return () => {
      socket.disconnect();
    };
  }, [assessmentId, questionId]);

  return (
    <div className='p-5 pt-2.5 mb-1'>
      <h1 className='text-lg font-semibold mb-2'>{question}</h1>
      <div className='pl-3'>
        <p>Scan the QR code and upload the photo from your phone or upload here directly</p>
        <p className='text-red-500 uppercase font-semibold'>
          Make Sure your handwritten is clear and is readable
        </p>
        {/* QR */}
        {uploadedImage && (
          <Image src={uploadedImage} alt='Uploaded Image' width={175} height={175} />
        )}
        <div className='flex gap-5'>
          <QRCode size={175} value={qrCodeUrl} />
          <Input type='file' className='hidden' id='fileInput' ref={ref} />
          <Button variant='secondary' className='mt-2' onClick={() => ref.current?.click()}>
            Upload
            <Upload className='size-4' />
          </Button>
        </div>
      </div>
    </div>
  );
}
