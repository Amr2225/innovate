import { Loader2 } from "lucide-react";

export default function Loader() {
  return (
    <div className='flex items-center justify-center h-[50vh]'>
      <Loader2 className='size-12 animate-spin text-primary' />
    </div>
  );
}
