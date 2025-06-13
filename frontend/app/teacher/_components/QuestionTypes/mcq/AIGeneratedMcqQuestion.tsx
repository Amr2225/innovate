import { useState } from "react";
import { useForm } from "react-hook-form";
import { useParams } from "next/navigation";

// Types
import { AIGeneratedMCQQuestion } from "@/types/assessment.type";

// Components
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card";
import { Info, Loader2 } from "lucide-react";
import CustomDialog from "@/components/CustomDialog";
import { DialogClose } from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

// API
import { getLectures } from "@/apiService/LectureService";
import { aiGeneratedMcqQuestion } from "@/apiService/assessmentService";
import { useMutation, useQuery } from "@tanstack/react-query";

// Store
import { createAssessmentStore } from "@/store/assessmentStore";

// Toast
import { toast } from "sonner";

// Components
import AIGeneratedMcqQuestionPreview from "./AIGeneratedMcqQuestionPreview";

export default function AIGeneratedMcqQuestion({ question }: { question: AIGeneratedMCQQuestion }) {
  const [dialogOpen, setDialogOpen] = useState<"addLectures" | "aiGeneratedMcq" | null>(null);

  const { courseId } = useParams();
  const useAssessmentStore = createAssessmentStore(courseId as string);
  const { updateQuestion, setAIGenerateMCQ, deleteAIGenerateMCQ } = useAssessmentStore();

  const { mutate: generateQuestion, isPending: isGenerating } = useMutation({
    mutationFn: () => aiGeneratedMcqQuestion({ question }),
    onSuccess: (data) => {
      toast.success("Question generated successfully");
      deleteAIGenerateMCQ(question.id);
      data.forEach((AIQuestion) => {
        setAIGenerateMCQ(
          question.id,
          AIQuestion.question,
          AIQuestion.options,
          AIQuestion.correct_answer,
          question.totalGrade || 0
        );
      });
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const form = useForm({
    defaultValues: {
      difficulty: question.difficulty || "",
      totalGrade: question.totalGrade || "",
      numberOfQuestions: question.numberOfQuestions || "",
      numberOfChoices: question.numberOfChoices || "",
    },
  });
  return (
    <div className='space-y-4'>
      <div className=''>
        <Form {...form}>
          <form className='space-y-4'>
            <FormField
              control={form.control}
              name='difficulty'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Difficulty</FormLabel>
                  <FormControl>
                    <Select
                      onValueChange={(value) =>
                        updateQuestion<AIGeneratedMCQQuestion>(question.id, "difficulty", value)
                      }
                      defaultValue={field.value || ""}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder='Select Difficulty' />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value='1'>Very Easy</SelectItem>
                        <SelectItem value='2'>Easy</SelectItem>
                        <SelectItem value='3'>Medium</SelectItem>
                        <SelectItem value='4'>Hard</SelectItem>
                        <SelectItem value='5'>Very Hard</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormControl>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name='numberOfQuestions'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Number of Questions</FormLabel>
                  <FormControl>
                    <Input
                      placeholder='Enter Number of Questions'
                      type='number'
                      {...field}
                      // value={question.numberOfQuestions || ""}
                      onBlur={(e) =>
                        updateQuestion<AIGeneratedMCQQuestion>(
                          question.id,
                          "numberOfQuestions",
                          e.target.value
                        )
                      }
                    />
                  </FormControl>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name='numberOfChoices'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Number of Choices Per Question</FormLabel>
                  <FormControl>
                    <Input
                      placeholder='Enter Number of Choices'
                      type='number'
                      min={2}
                      max={6}
                      {...field}
                      value={question.numberOfChoices || ""}
                      onChange={(e) => {
                        const value = parseInt(e.target.value);
                        if (value >= 2 && value <= 6) {
                          updateQuestion<AIGeneratedMCQQuestion>(
                            question.id,
                            "numberOfChoices",
                            value.toString()
                          );
                        }
                        if (value < 2 || !value) {
                          updateQuestion<AIGeneratedMCQQuestion>(
                            question.id,
                            "numberOfChoices",
                            ""
                          );
                        }
                      }}
                    />
                  </FormControl>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name='totalGrade'
              render={({ field }) => (
                <FormItem>
                  <div className='flex items-center gap-1.5'>
                    <FormLabel>Total Grade</FormLabel>
                    <HoverCard>
                      <HoverCardTrigger asChild>
                        <Info className='size-3.5 text-neutral-500 cursor-help' />
                      </HoverCardTrigger>
                      <HoverCardContent className='w-80'>
                        <div className='space-y-2'>
                          <h4 className='text-sm font-semibold'>Total Grade</h4>
                          <p className='text-sm text-muted-foreground'>
                            The total grade represents the maximum points for all questions
                            combined. Each individual question&apos;s grade will be automatically
                            calculated by dividing this total by the number of questions.
                          </p>
                        </div>
                      </HoverCardContent>
                    </HoverCard>
                  </div>
                  <FormControl>
                    <Input
                      placeholder='Enter Total Grade for all the questions'
                      type='number'
                      {...field}
                      onBlur={(e) =>
                        updateQuestion<AIGeneratedMCQQuestion>(
                          question.id,
                          "totalGrade",
                          e.target.value
                        )
                      }
                    />
                  </FormControl>
                </FormItem>
              )}
            />
          </form>
        </Form>
      </div>

      <div className='flex gap-2 items-center w-full'>
        <Button className='w-full' onClick={() => setDialogOpen("addLectures")}>
          Choose From Lectures
        </Button>

        {question.questions && question.questions.length > 0 && (
          <Button
            className='w-[20%]'
            variant='secondary'
            onClick={() => setDialogOpen("aiGeneratedMcq")}
          >
            View AI Generated MCQ
          </Button>
        )}

        <Button
          className='w-[10%]'
          variant='link'
          onClick={() => generateQuestion()}
          disabled={isGenerating}
        >
          {isGenerating ? (
            <Loader2 className='size-4 animate-spin' />
          ) : (
            <HoverCard>
              <HoverCardTrigger asChild>
                <span className='flex items-center gap-1'>
                  <p>Generate</p>
                  <Info className='size-3 text-primary  cursor-help' />
                </span>
              </HoverCardTrigger>
              <HoverCardContent className=''>
                <div className='space-y-2'>
                  <h4 className='text-sm font-semibold'>AI Generate Questions</h4>
                  <p className='text-sm text-muted-foreground text-wrap'>
                    AI generated MCQ questions must be generated first before saving the assessment.
                  </p>
                </div>
              </HoverCardContent>
            </HoverCard>
          )}
        </Button>
      </div>

      {/* Add Lectures */}
      <CustomDialog
        title='Add Lectures'
        description='Add lectures for the question'
        open={dialogOpen === "addLectures"}
        setOpen={(open) => setDialogOpen(open ? "addLectures" : null)}
      >
        <div>
          <LectureSelector question={question} />
        </div>
        <div className='flex justify-between items-center gap-2'>
          <div className='space-x-2'>
            <DialogClose asChild>
              <Button type='button' variant='secondary'>
                Close
              </Button>
            </DialogClose>
          </div>
          {/* <Button>Upload</Button> */}
        </div>
      </CustomDialog>

      {/* AI Generated MCQ */}
      <CustomDialog
        title='AI Generated MCQ'
        description='Add lectures for the question'
        contentClassName='max-w-[80%]'
        open={dialogOpen === "aiGeneratedMcq"}
        setOpen={(open) => setDialogOpen(open ? "aiGeneratedMcq" : null)}
      >
        <AIGeneratedMcqQuestionPreview
          AIQuestions={question.questions}
          AIQuestionId={question.id}
        />
        <div className='flex justify-between items-center gap-2 mt-2'>
          <DialogClose asChild>
            <Button type='button' variant='secondary'>
              Close
            </Button>
          </DialogClose>
          <div className='flex items-center gap-2'>
            <Button>Save</Button>
            <Button
              variant='link'
              onClick={() => {
                deleteAIGenerateMCQ(question.id);
                generateQuestion();
              }}
            >
              {isGenerating ? <Loader2 className='size-4 animate-spin' /> : "Regenerate"}
            </Button>
          </div>
        </div>
      </CustomDialog>
    </div>
  );
}

function LectureSelector({ question }: { question: AIGeneratedMCQQuestion }) {
  const params = useParams();
  const courseId = params.courseId as string;

  const useAssessmentStore = createAssessmentStore(courseId as string);
  const { updateQuestion } = useAssessmentStore();

  const { data: lectures, isLoading } = useQuery({
    queryKey: ["lectures"],
    queryFn: () => getLectures({ page_size: 1000, courseId }),
  });

  if (isLoading) return <Loader2 className='size-4 animate-spin' />;

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
                updateQuestion<AIGeneratedMCQQuestion>(question.id, "lectures", [
                  ...currentValues,
                  lecture.id,
                ]);
              } else {
                updateQuestion<AIGeneratedMCQQuestion>(
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
