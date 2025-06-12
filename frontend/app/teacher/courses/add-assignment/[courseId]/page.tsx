"use client";
import React from "react";
import { useParams } from "next/navigation";
import { Reorder } from "framer-motion";

// Components
import { Button } from "@/components/ui/button";
import QuestionContainer from "@/app/teacher/_components/questionContainer";
import AssessmentTabs from "@/app/teacher/_components/assessmentTabs";
import { TabsContent } from "@/components/ui/tabs";

// Store
import { createAssessmentStore } from "@/store/assessmentStore";

// Icons
import { Plus } from "lucide-react";

export default function AddAssignmentPage() {
  // const [sectionKey, setSectionKey] = useState("");
  const { courseId } = useParams();

  const useAssessmentStore = createAssessmentStore(courseId as string);
  const { questions, setQuestions, addQuestion, currentSection, sections } = useAssessmentStore();

  // useEffect(() => {
  //   setTimeout(() => {
  //     setSectionKey(`section-${currentSection}`);
  //   }, 200);
  // }, [currentSection]);

  return (
    <AssessmentTabs defaultSection={`section-${sections[0].id}`}>
      <TabsContent value={`section-${currentSection}`}>
        <Reorder.Group
          axis='y'
          values={questions}
          onReorder={(questions) => setQuestions(questions)}
        >
          {questions
            .filter((question) => question.sectionNumber === currentSection)
            .map((question, index) => (
              <QuestionContainer key={question.id} question={question} questionNumber={index + 1} />
            ))}
        </Reorder.Group>
      </TabsContent>
      <Button variant='secondary' className='w-full py-5 font-semibold mt-2' onClick={addQuestion}>
        <Plus className='size-5 mr-1' />
        Add Question
      </Button>
    </AssessmentTabs>
  );
}
