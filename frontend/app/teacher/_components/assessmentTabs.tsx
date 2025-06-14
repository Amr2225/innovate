import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAssessmentStore } from "@/store/assessmentStore";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { CirclePlus, Trash } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  ContextMenu,
  ContextMenuItem,
  ContextMenuContent,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
import { useEffect, useState } from "react";

export default function AssessmentTabs({ children }: { children: React.ReactNode }) {
  const [firstSection, setFirstSection] = useState<string>("");
  const { sections, setCurrentSection, addSection, deleteSection } = useAssessmentStore();

  useEffect(() => {
    if (sections.length > 0) {
      setTimeout(() => {
        setFirstSection(`section-${sections[0].id}`);
      }, 200);
    }
  }, [sections, setFirstSection]);

  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className='p-4 w-full h-full'
    >
      <h1 className='text-2xl font-bold mb-4'>Add Assignment</h1>

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
