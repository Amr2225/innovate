"use client";
import { useState, useRef, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useMutation } from "@tanstack/react-query";
import { addTempHandwrittenImage } from "@/apiService/tempHandwrittenImage";
import { toast } from "sonner";

export default function UploadPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const assessmentId = searchParams.get("assessmentId") || "";
  const questionId = searchParams.get("questionId") || "";
  const token = searchParams.get("token") || "";

  const {
    mutate: addTempHandwrittenImageMutation,
    isPending,
    isSuccess: uploadSuccess,
  } = useMutation({
    mutationFn: ({ formData }: { formData: FormData }) =>
      addTempHandwrittenImage({ formData, assessmentId, questionId, token }),
    onSuccess: () => {
      toast.success("Upload successful");
      console.log("Upload successful");
    },
    onError: (error) => {
      toast.error(`Upload failed: ${JSON.stringify(error)}`);
      console.log("Upload failed", error);
    },
  });

  // Request camera access when component mounts
  useEffect(() => {
    requestCameraPermission();

    // Clean up function to stop camera stream when component unmounts
    return () => {
      if (cameraStream) {
        cameraStream.getTracks().forEach((track) => track.stop());
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Function to request camera permission
  const requestCameraPermission = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "environment",
          width: { min: 1280, max: 1920 },
          height: { min: 720, max: 1080 },
          frameRate: { min: 30, max: 60 },
        },
      });

      setCameraStream(stream);

      // Connect video element to stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error("Camera permission error:", err);
      if (err instanceof DOMException && err.name === "NotAllowedError") {
        setError("Camera access denied. Please grant permission to use your camera.");
      } else if (err instanceof DOMException && err.name === "NotFoundError") {
        setError("No camera found on your device.");
      } else {
        setError("Error accessing camera. Please try again.");
      }
    }
  };

  // Function to capture photo
  const capturePhoto = async () => {
    if (!videoRef.current || !canvasRef.current || !cameraStream) {
      setError("Camera not ready. Please try again.");
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw current video frame to canvas
    context?.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to image data
    const imageData = canvas.toDataURL("image/jpeg");

    // Convert data URL to Blob
    const fetchResponse = await fetch(imageData);
    const blob = await fetchResponse.blob();

    // Create a File object
    const imageFile = new File([blob], "image.jpg", { type: "image/jpeg" });

    // Upload the image
    const formData = new FormData();
    formData.append("image", imageFile);
    addTempHandwrittenImageMutation({ formData });
  };

  // Retry camera access
  const retryCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach((track) => track.stop());
    }
    requestCameraPermission();
  };

  return (
    <div className='p-4 flex flex-col items-center justify-center min-h-screen bg-slate-50'>
      <h1 className='text-2xl font-bold mb-4'>Upload Your Answer</h1>
      <p className='mb-6 text-center'>
        Take a photo of your handwritten answer for Question #{questionId}
      </p>

      {error && (
        <div className='mb-4 p-3 bg-red-100 text-red-700 rounded-md text-center'>
          {error}
          <Button onClick={retryCamera} variant='outline' className='mt-2 w-full'>
            Retry Camera Access
          </Button>
        </div>
      )}

      {!uploadSuccess ? (
        <div className='w-full max-w-md flex flex-col items-center'>
          {/* Camera preview */}
          <div className='relative w-full aspect-[3/4] bg-black rounded-md overflow-hidden mb-4'>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={`w-full h-full object-cover ${!cameraStream ? "hidden" : ""}`}
              style={{
                transform: "scaleX(1)",
                willChange: "transform",
              }}
            />

            {!cameraStream && !error && (
              <div className='absolute inset-0 flex items-center justify-center text-white'>
                Loading camera...
              </div>
            )}

            {/* Hidden canvas for capturing image */}
            <canvas ref={canvasRef} className='hidden' />
          </div>

          {/* Capture button */}
          <div className='flex gap-3 w-full'>
            <Button
              onClick={capturePhoto}
              disabled={isPending || !cameraStream}
              className='flex-1 h-12 text-lg'
            >
              {isPending ? "Uploading..." : "Capture Photo"}
            </Button>

            <Button
              variant='outline'
              onClick={() => router.push(`/student/assessment/${assessmentId}`)}
              className='h-12'
            >
              Cancel
            </Button>
          </div>
        </div>
      ) : (
        <div className='text-center p-6 bg-white rounded-lg shadow-sm'>
          <div className='text-green-600 text-5xl mb-4'>✓</div>
          <h2 className='text-xl text-green-600 mb-2'>Upload Successful!</h2>
          <p className='mb-4'>
            Your answer has been submitted and will appear on your assessment page.
          </p>
          <Button className='w-full' onClick={() => window.close()}>
            Close
          </Button>
        </div>
      )}
    </div>
  );
}
