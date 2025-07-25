import { Button } from "@/components/ui/button";
import { type DynamicMCQQuestion } from "@/types/assessment.type";
import { useForm } from "react-hook-form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Form, FormControl, FormField, FormItem, FormLabel } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card";
import { Info } from "lucide-react";

import CustomDialog from "@/components/CustomDialog";
import { useState } from "react";
import { DialogClose } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { useParams } from "next/navigation";
import { createAssessmentStore } from "@/store/assessmentStore";
import LectureSelector from "./lectureSelector";

export default function DynamicMCQQuestion({ question }: { question: DynamicMCQQuestion }) {
  const [dialogOpen, setDialogOpen] = useState<"addContext" | "addLectures" | null>(null);

  const { assessmentId } = useParams();
  const useAssessmentStore = createAssessmentStore(assessmentId as string);
  const { updateQuestion } = useAssessmentStore();

  const form = useForm({
    defaultValues: {
      difficulty: question.difficulty || "",
      totalGrade: question.totalGrade || "",
      numberOfQuestions: question.numberOfQuestions || "",
      numberOfChoices: question.numberOfChoices || "",
    },
  });
  return (
    <div className='grid grid-cols-3 items-center'>
      <div className='w-[70%] col-span-2'>
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
                        updateQuestion<DynamicMCQQuestion>(question.id, "difficulty", value)
                      }
                      defaultValue={field.value!}
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
                      onBlur={(e) =>
                        updateQuestion<DynamicMCQQuestion>(
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
                          updateQuestion<DynamicMCQQuestion>(
                            question.id,
                            "numberOfChoices",
                            value.toString()
                          );
                        }
                        if (value < 2 || !value) {
                          updateQuestion<DynamicMCQQuestion>(question.id, "numberOfChoices", "");
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
                        updateQuestion<DynamicMCQQuestion>(
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

      <div className='w-full col-span-1'>
        <Button className='w-full' onClick={() => setDialogOpen("addContext")}>
          Add Context
        </Button>
        <div className='flex items-center gap-2'>
          <div className='h-[1px] bg-neutral-200 flex-1'></div>
          <span className='text-sm text-neutral-500'>OR</span>
          <div className='h-[1px] bg-neutral-200 flex-1'></div>
        </div>
        <Button className='w-full' onClick={() => setDialogOpen("addLectures")}>
          Choose From Lectures
        </Button>
      </div>

      {/* Add Context */}
      <CustomDialog
        title='Add Context'
        description='Add a context for the question'
        open={dialogOpen === "addContext"}
        setOpen={(open) => setDialogOpen(open ? "addContext" : null)}
      >
        <div>
          <Textarea
            onBlur={(e) =>
              e.target.value.trim() !== "" &&
              updateQuestion<DynamicMCQQuestion>(question.id, "context", e.target.value)
            }
            defaultValue={question.context || ""}
            placeholder='Enter Context'
            className='min-h-[200px]'
          />
        </div>
        <div className='flex justify-between items-center gap-2 mt-2'>
          <div className='space-x-2'>
            <DialogClose asChild>
              <Button type='button' variant='secondary'>
                Close
              </Button>
            </DialogClose>
          </div>
        </div>
      </CustomDialog>

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
        <div className='flex justify-between items-center gap-2 mt-2'>
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
    </div>
  );
}
