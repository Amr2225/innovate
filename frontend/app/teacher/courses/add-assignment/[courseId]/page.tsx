"use client";
import React from "react";
import { Reorder } from "framer-motion";

// Components
import { Button } from "@/components/ui/button";
import QuestionContainer from "@/app/teacher/_components/questionContainer";
import AssessmentTabs from "@/app/teacher/_components/assessmentTabs";
import { TabsContent } from "@/components/ui/tabs";

// Store
import { useAssessmentStore } from "@/store/assessmentStore";

// Icons
import { Plus } from "lucide-react";

export default function AddAssignmentPage() {
  const { questions, setQuestions, addQuestion, currentSection } = useAssessmentStore();

  return (
    <AssessmentTabs>
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
