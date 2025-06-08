import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
// import { useAssessmentStore } from "@/store/assessmentStore";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { CirclePlus, Loader2, Trash } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  ContextMenu,
  ContextMenuItem,
  ContextMenuContent,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
import { useEffect, useState } from "react";
import { createAssessmentStore } from "@/store/assessmentStore";
import { useParams } from "next/navigation";

import DatePicker from "@/components/date-picker";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { useAssessmentQuery } from "@/queryHooks/useAssessment";

export default function AssessmentTabs({ children }: { children: React.ReactNode }) {
  const [firstSection, setFirstSection] = useState<string>("");
  const { handleCreateAssessment, isCreating } = useAssessmentQuery();

  const { courseId } = useParams();

  const useAssessmentStore = createAssessmentStore(courseId as string);
  const {
    sections,
    setCurrentSection,
    addSection,
    deleteSection,
    title,
    grade,
    start_date,
    due_date,
    updateAssessment,
  } = useAssessmentStore();

  useEffect(() => {
    if (sections.length > 0) {
      setTimeout(() => {
        setFirstSection(`section-${sections[0].id}`);
      }, 300);
    }
  }, [sections, setFirstSection]);

  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className='p-4 w-full h-full'
    >
      <div className='flex flex-col md:flex-row items-center md:items-center justify-between w-full mb-5'>
        <h1 className='text-2xl font-bold mb-4 whitespace-nowrap'>Add Assignment</h1>

        <div className='grid md:grid-cols-[1fr_1fr_1fr_1fr_0.12fr] items-end grid-cols-1 gap-3'>
          <div className='flex flex-col items-start gap-2'>
            <Label>Title</Label>
            <Input
              type='text'
              placeholder='Enter Title'
              defaultValue={title}
              onBlur={(e) => updateAssessment("title", e.target.value)}
            />
          </div>
          <div className='flex flex-col items-start gap-2'>
            <Label>Grade</Label>
            <Input
              type='number'
              placeholder='Enter Grade'
              defaultValue={grade}
              onBlur={(e) => updateAssessment("grade", e.target.value)}
            />
          </div>

          <div className='flex flex-col items-start gap-2'>
            <Label>Start Date</Label>
            <DatePicker
              date={start_date as Date}
              setDate={(date) => updateAssessment("start_date", date as string)}
            />
          </div>

          <div className='flex flex-col items-start gap-2'>
            <Label>Due Date</Label>
            <DatePicker
              date={due_date}
              setDate={(date) => updateAssessment("due_date", date as string)}
            />
          </div>

          <Button
            variant='default'
            className='mt-4 w-full self-end'
            onClick={handleCreateAssessment}
            disabled={isCreating}
          >
            {isCreating ? <Loader2 className='size-4 animate-spin' /> : "Upload"}
          </Button>
        </div>
      </div>

      <Tabs
        key={firstSection}
        defaultValue={firstSection}
        onValueChange={(value) => setCurrentSection(Number(value.split("-")[1]))}
      >
        <motion.div
          className='w-full flex items-center gap-2'
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.2 }}
          layout
        >
          <TabsList className={cn("grid w-full grid-cols-1", `grid-cols-${sections.length}`)}>
            {sections.map((section, index) => (
              <ContextMenu key={section.id}>
                <TabsTrigger className='cursor-pointer' value={`section-${section.id}`} asChild>
                  <ContextMenuTrigger>Section {index + 1}</ContextMenuTrigger>
                </TabsTrigger>
                <ContextMenuContent>
                  <ContextMenuItem
                    className='cursor-pointer'
                    onSelect={() => deleteSection(section.id)}
                  >
                    <Trash className='size-4 mr-2' />
                    Delete Section
                  </ContextMenuItem>
                </ContextMenuContent>
              </ContextMenu>
            ))}
          </TabsList>
          <Button variant='ghost' size='icon' className='p-2' onClick={addSection}>
            <CirclePlus className='size-5' />
          </Button>
        </motion.div>

        {children}
      </Tabs>
    </motion.section>
  );
}
