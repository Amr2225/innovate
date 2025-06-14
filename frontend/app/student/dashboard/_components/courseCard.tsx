import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";

export default function courseCard() {
  return (
    <div className='w-full h-full border border-neutral-200 rounded-md'>
      <span className='w-[200px] block h-[100px] bg-white rounded-full' />
      <div className='flex flex-col items-start justify-center px-3 py-1'>
        <h4 className='font-bold text-sm'>Course Name</h4>
        <p className='text-sm text-gray-500'>Course Description</p>
      </div>
      <Separator />
      <div className='px-3 p-2'>
        <Button type='button' variant='default' className='w-full'>
          Watch Lecture
        </Button>
      </div>
    </div>
  );
}
