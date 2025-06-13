import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function courseCard({
  courseName,
  courseDescription,
  courseId,
}: {
  courseName: string;
  courseDescription: string;
  courseId: string;
}) {
  return (
    <div className='w-full h-full border border-neutral-200 rounded-md'>
      <div className='w-full h-[100px] bg-gradient-to-br from-orange-200 to-orange-400 rounded-t-md flex items-center justify-center'>
        <span className='text-3xl font-bold text-white'>
          {courseName
            .split(" ")
            .map((word) => word[0])
            .join("")
            .toUpperCase()
            .slice(0, 3)}
        </span>
      </div>
      <div className='flex flex-col items-start justify-center px-3 py-1'>
        <h4 className='font-bold text-base py-2 pb-1'>{courseName}</h4>
        <p className='text-sm text-gray-500'>{courseDescription}</p>
      </div>
      <Separator />
      <div className='px-3 py-2'>
        <Button type='button' variant='default' className='w-full' asChild>
          <Link href={`/student/watch/${courseId}`}>Watch Lecture</Link>
        </Button>
      </div>
    </div>
  );
}
