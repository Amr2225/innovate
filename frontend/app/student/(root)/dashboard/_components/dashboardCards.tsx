import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card";
import { cn } from "@/lib/utils";
import CountUp from "react-countup";

interface DashboardCardsProps {
  count: number;
  title: string;
  color: string;
  iconColor: string;
  submitted_assignments_count: number;
  submitted_quizzes_count: number;
  submitted_exams_count: number;
  isHover: boolean;
  Icon: React.ElementType;
}

export default function DashboardCards({
  count,
  title,
  color,
  Icon,
  iconColor,
  submitted_assignments_count,
  submitted_quizzes_count,
  submitted_exams_count,
  isHover,
}: DashboardCardsProps) {
  return (
    <div
      className={cn(
        "w-full h-full mt-2 ",
        isHover && "hover:scale-105 transition-all duration-300 cursor-pointer"
      )}
    >
      {isHover ? (
        <HoverCard>
          <HoverCardTrigger>
            <div
              className={cn(
                "p-3 w-full h-full flex items-center justify-start gap-3 rounded-md",
                color
              )}
            >
              <span className='p-2 rounded-full bg-white'>
                <Icon className={iconColor} />
              </span>
              <div className='flex flex-col'>
                <h1 className='text-xl'>
                  <CountUp end={count} />
                </h1>
                <p className='text-sm font-semibold text-black/60'>{title}</p>
              </div>
            </div>
          </HoverCardTrigger>
          <HoverCardContent className='w-80'>
            <div className='flex justify-between space-x-4'>
              <div className='space-y-1'>
                <h4 className='text-sm font-semibold'>Submitted Assessments</h4>
                <div className='flex items-center pt-2'>
                  <span className='text-sm text-muted-foreground'>
                    Assignments: {submitted_assignments_count}
                  </span>
                </div>
                <div className='flex items-center pt-2'>
                  <span className='text-sm text-muted-foreground'>
                    Quizzes: {submitted_quizzes_count}
                  </span>
                </div>
                <div className='flex items-center pt-2'>
                  <span className='text-sm text-muted-foreground'>
                    Exams: {submitted_exams_count}
                  </span>
                </div>
              </div>
            </div>
          </HoverCardContent>
        </HoverCard>
      ) : (
        <div
          className={cn(
            "p-3 w-full h-full flex items-center justify-start gap-3 rounded-md",
            color
          )}
        >
          <span className='p-2 rounded-full bg-white'>
            <Icon className={iconColor} />
          </span>
          <div className='flex flex-col'>
            <h1 className='text-xl'>
              <CountUp end={count} />
            </h1>
            <p className='text-sm font-semibold text-black/60'>{title}</p>
          </div>
        </div>
      )}
    </div>
  );
}
