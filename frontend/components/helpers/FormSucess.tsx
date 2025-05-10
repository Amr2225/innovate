import { CircleCheck } from "lucide-react";

interface FromSuccessProps {
  message?: string;
}

export function FormSuccess({ message }: FromSuccessProps) {
  if (!message) return null;
  return (
    <div className='bg-emerald-500/15 p-3 rounded-md flex items-center gap-x-2 text-sm text-emerald-500'>
      <CircleCheck className='size-4' />
      <p>{message}</p>
    </div>
  );
}
