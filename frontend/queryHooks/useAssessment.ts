'use client'
import { createAssessment, dynamicMcqQuestion, handwrittenQuestion, mcqQuestion } from "@/apiService/assessmentService";
import { createAssessmentStore } from "@/store/assessmentStore";
import { Question } from "@/types/assessment.type";
import { useMutation } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useMemo } from "react";
import { toast } from "sonner";

export function useAssessmentQuery() {
    const { courseId } = useParams();
    const useAssessmentStore = createAssessmentStore(courseId as string);
    const { title, type, due_date, start_date, grade, questions } = useAssessmentStore();

    const { mutate: createAssessmentMutation, isPending: isCreatingAssessment } = useMutation({
        mutationFn: () => createAssessment({ courseId: courseId as string, title, type, due_date, start_date, grade }),
        onSuccess: (data) => {
            toast.success("Assessment created successfully");
            console.log("assessmentData", data);

            questions.forEach((question) => {
                switch (question.questionType) {
                    case "dynamicMcq":
                        createDynamicMcqQuestionMutation({ question, assessmentId: data.id });
                        break;
                    case "handWritten":
                        createHandwrittenQuestionMutation({ question, assessmentId: data.id });
                        break;
                    case "mcq":
                        createMcqQuestionMutation({ question, assessmentId: data.id });
                        break;
                    default:
                        console.log("Unknown question type:", question.questionType);
                }
            })
        },
        onError: (error) => {
            console.log(error);
        },
    })

    // Dynamic MCQ
    const { mutate: createDynamicMcqQuestionMutation, isPending: isCreatingDynamicMcqQuestion } = useMutation({
        mutationFn: ({ question, assessmentId }: { question: Question, assessmentId: string }) => dynamicMcqQuestion({ question, assessmentId }),
        onSuccess: (data) => {
            toast.success("Dynamic Mcq Question created successfully");
            console.log("dynamicMcqQuestionData", data);
        },
        onError: (error) => {
            console.log(error);
        },
    })

    // MCQ
    const { mutate: createMcqQuestionMutation, isPending: isCreatingMcqQuestion } = useMutation({
        mutationFn: ({ question, assessmentId }: { question: Question, assessmentId: string }) => mcqQuestion({ question, assessmentId }),
        onSuccess: (data) => {
            toast.success("Mcq Question created successfully");
            console.log("mcqQuestionData", data);
        },
        onError: (error) => {
            console.log(error);
        },
    })

    // Handwritten
    const { mutate: createHandwrittenQuestionMutation, isPending: isCreatingHandwrittenQuestion } = useMutation({
        mutationFn: ({ question, assessmentId }: { question: Question, assessmentId: string }) => handwrittenQuestion({ question, assessmentId }),
        onSuccess: (data) => {
            toast.success("Handwritten Question created successfully");
            console.log("handwrittenQuestionData", data);
        },
        onError: (error) => {
            console.log(error);
        },
    })

    const isCreating = useMemo(() => {
        return isCreatingAssessment || isCreatingDynamicMcqQuestion || isCreatingMcqQuestion || isCreatingHandwrittenQuestion;
    }, [isCreatingAssessment, isCreatingDynamicMcqQuestion, isCreatingMcqQuestion, isCreatingHandwrittenQuestion])

    const handleCreateAssessment = () => {
        createAssessmentMutation();

    }


    return { handleCreateAssessment, isCreating }
}
