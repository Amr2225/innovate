import { AIGeneratedMCQQuestion, DynamicMCQQuestion } from "@/types/assessment.type";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuCheckboxItem,
} from "@/components/ui/dropdown-menu";

import { getLectures } from "@/apiService/LectureService";
import { createAssessmentStore } from "@/store/assessmentStore";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";

import { useParams } from "next/navigation";
import { Skeleton } from "@/components/ui/skeleton";

export default function LectureSelector({
  question,
}: {
  question: DynamicMCQQuestion | AIGeneratedMCQQuestion;
}) {
  const { assessmentId } = useParams();
  const useAssessmentStore = createAssessmentStore(assessmentId as string);
  const { updateQuestion, courseId } = useAssessmentStore();

  const { data: lectures, isLoading } = useQuery({
    queryKey: ["lectures"],
    queryFn: () => getLectures({ page_size: 1000, courseId }),
  });

  if (isLoading) return <Skeleton className='w-full h-10' />;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant='outline' className='w-full justify-between'>
          Select Lectures
          <span className='ml-2 opacity-70'>
            {Array.isArray(question.lectures) && question.lectures.length > 0
              ? `${question.lectures.length} selected`
              : "None"}
          </span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        className='max-h-full overflow-auto'
        sideOffset={4}
        style={{ width: "var(--radix-dropdown-menu-trigger-width)" }}
      >
        <DropdownMenuLabel>Select Lectures</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {lectures?.map((lecture) => (
          <DropdownMenuCheckboxItem
            key={lecture.id}
            className='hover:bg-neutral-100 cursor-pointer'
            checked={
              Array.isArray(question.lectures) && question.lectures.includes(lecture.id || "")
            }
            onCheckedChange={(checked) => {
              const currentValues = Array.isArray(question.lectures) ? question.lectures : [];
              if (checked) {
                updateQuestion<DynamicMCQQuestion>(question.id, "lectures", [
                  ...currentValues,
                  lecture.id,
                ]);
              } else {
                updateQuestion<DynamicMCQQuestion>(
                  question.id,
                  "lectures",
                  currentValues.filter((id) => id !== lecture.id)
                );
              }
            }}
          >
            {lecture.title}
          </DropdownMenuCheckboxItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
