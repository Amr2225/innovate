import { useParams } from "next/navigation";
import { motion } from "framer-motion";

// Icons
import { CirclePlus, Loader2, Trash } from "lucide-react";

// Components
import { Button } from "@/components/ui/button";
import {
  ContextMenu,
  ContextMenuItem,
  ContextMenuContent,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
  AlertDialogCancel,
  AlertDialogAction,
} from "@/components/ui/alert-dialog";

// Utils and Hooks
import { cn } from "@/lib/utils";
import { useAssessmentQuery } from "@/queryHooks/useAssessment";
import { createAssessmentStore } from "@/store/assessmentStore";

export default function AssessmentTabs({
  defaultSection,
  children,
}: {
  defaultSection: `section-${string}`;
  children: React.ReactNode;
}) {
  // const [firstSection, setFirstSection] = useState<string>("");
  const { handleCreateAssessment, isCreating } = useAssessmentQuery();

  const { assessmentId } = useParams();

  const useAssessmentStore = createAssessmentStore(assessmentId as string);
  const { sections, setCurrentSection, addSection, deleteSection, getTotalGrade } =
    useAssessmentStore();

  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className='p-4 w-full h-full'
    >
      <div className='flex flex-col md:flex-row items-center md:items-center justify-between w-full mb-5'>
        <div>
          <h1 className='text-2xl font-bold mb-2 whitespace-nowrap'>Add Questions</h1>
          <div className='text-sm font-medium text-muted-foreground mb-2'>
            Assessment Total Grade: {getTotalGrade()}
          </div>
        </div>

        <div>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant='default' className='mt-4 w-full self-end' disabled={isCreating}>
                {isCreating ? <Loader2 className='size-4 animate-spin' /> : "Upload"}
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will create the assessment with all the questions and sections.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleCreateAssessment}>Continue</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>

      <Tabs
        key={defaultSection}
        defaultValue={defaultSection}
        onValueChange={(value) => setCurrentSection(value.split("-")[1])}
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
