import { cn } from "@/lib/utils";

interface DashboardCardsProps {
  count: number;
  title: string;
  color: string;
  Icon: React.ElementType;
  iconColor: string;
}

export default function DashboardCards({
  count,
  title,
  color,
  Icon,
  iconColor,
}: DashboardCardsProps) {
  return (
    <div className='w-full h-full mt-2'>
      <div
        className={cn("p-3 w-full h-full flex items-center justify-start gap-3 rounded-md", color)}
      >
        <span className='p-2 rounded-full bg-white'>
          <Icon className={iconColor} />
        </span>
        <div className='flex flex-col'>
          <h1 className='text-xl'>{count}</h1>
          <p className='text-sm font-semibold text-black/60'>{title}</p>
        </div>
      </div>
    </div>
  );
}
