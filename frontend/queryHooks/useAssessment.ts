'use client'
import { useMemo } from "react";
import { useParams } from "next/navigation";
import { toast } from "sonner";

// API 
import { createAssessment, dynamicMcqQuestion, handwrittenQuestion, mcqQuestion, saveAIGeneratedMcqQuestion } from "@/apiService/assessmentService";
import { useMutation } from "@tanstack/react-query";

// Store
import { createAssessmentStore } from "@/store/assessmentStore";

// Types
import { DynamicMCQQuestion, MCQQuestion, HandWrittenQuestion, AIGeneratedMCQQuestion } from "@/types/assessment.type";


export function useAssessmentQuery() {
    const { courseId } = useParams();
    const useAssessmentStore = createAssessmentStore(courseId as string);
    const { title, type, due_date, start_date, grade, questions, sections } = useAssessmentStore();

    const { mutate: createAssessmentMutation, isPending: isCreatingAssessment } = useMutation({
        mutationFn: () => createAssessment({ courseId: courseId as string, title, type, due_date, start_date, grade }),
        onSuccess: (data) => {
            toast.success("Assessment created successfully");
            console.log("assessmentData", data);

            questions.forEach((question) => {
                switch (question.questionType) {
                    case "dynamicMcq":
                        createDynamicMcqQuestionMutation({ question, assessmentId: data.id, sections: sections });
                        break;
                    case "handWritten":
                        createHandwrittenQuestionMutation({ question, assessmentId: data.id });
                        break;
                    case "mcq":
                        createMcqQuestionMutation({ question, assessmentId: data.id });
                        break;
                    case "aiMcq":
                        createAIGeneratedMcqQuestionMutation({ question: question, assessmentId: data.id, sections: sections });
                        break;
                    default:
                        console.log("Unknown question type:", question.questionType);
                }
            })
        },
        onError: (error) => {
            toast.error(`${error.message} (Assessment)`);
            console.log(error.message);
        },
    })

    // Dynamic MCQ
    const { mutate: createDynamicMcqQuestionMutation, isPending: isCreatingDynamicMcqQuestion } = useMutation({
        mutationFn: ({ question, assessmentId, sections }: { question: DynamicMCQQuestion, assessmentId: string, sections: { id: string }[] }) => dynamicMcqQuestion({ question, assessmentId, sections }),
        onSuccess: (data) => {
            toast.success("Dynamic Mcq Question created successfully");
            console.log("dynamicMcqQuestionData", data);
        },
        onError: (error) => {
            toast.error(`${error.message} (Dynamic MCQ)`);
            console.log(error.message);
        },
    })

    // MCQ
    const { mutate: createMcqQuestionMutation, isPending: isCreatingMcqQuestion } = useMutation({
        mutationFn: ({ question, assessmentId }: { question: MCQQuestion, assessmentId: string }) => mcqQuestion({ question, assessmentId }),
        onSuccess: (data) => {
            toast.success("Mcq Question created successfully");
            console.log("mcqQuestionData", data);
        },
        onError: (error) => {
            toast.error(`${error.message} (MCQ)`);
            console.log(error.message);
        },
    })

    // Handwritten
    const { mutate: createHandwrittenQuestionMutation, isPending: isCreatingHandwrittenQuestion } = useMutation({
        mutationFn: ({ question, assessmentId }: { question: HandWrittenQuestion, assessmentId: string }) => handwrittenQuestion({ question, assessmentId }),
        onSuccess: (data) => {
            toast.success("Handwritten Question created successfully");
            console.log("handwrittenQuestionData", data);
        },
        onError: (error) => {
            toast.error(`${error.message} (Handwritten)`);
            console.log(error.message);
        },
    })

    // AI Generated MCQ
    const { mutate: createAIGeneratedMcqQuestionMutation, isPending: isCreatingAIGeneratedMcqQuestion } = useMutation({
        mutationFn: ({ question, assessmentId, sections }: { question: AIGeneratedMCQQuestion, assessmentId: string, sections: { id: string }[] }) => saveAIGeneratedMcqQuestion({ question, assessmentId, sections }),
        onSuccess: (data) => {
            toast.success("AI Generated Mcq Question created successfully");
            console.log("aiGeneratedMcqQuestionData", data);
        },
        onError: (error) => {
            toast.error(`${error.message} (AI Generated MCQ)`);
            console.log(error.message);
        },
    })

    const isCreating = useMemo(() => {
        return isCreatingAssessment || isCreatingDynamicMcqQuestion || isCreatingMcqQuestion || isCreatingHandwrittenQuestion || isCreatingAIGeneratedMcqQuestion;
    }, [isCreatingAssessment, isCreatingDynamicMcqQuestion, isCreatingMcqQuestion, isCreatingHandwrittenQuestion, isCreatingAIGeneratedMcqQuestion])

    const handleCreateAssessment = () => {
        createAssessmentMutation();

    }


    return { handleCreateAssessment, isCreating }
}
