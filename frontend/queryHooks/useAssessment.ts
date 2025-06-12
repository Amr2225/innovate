'use client'
import { useMemo } from "react";
import { useParams, useRouter } from "next/navigation";
import { toast } from "sonner";

// API 
import { dynamicMcqQuestion, handwrittenQuestion, mcqQuestion, saveAIGeneratedMcqQuestion } from "@/apiService/assessmentService";
import { useMutation } from "@tanstack/react-query";

// Store
import { createAssessmentStore, deleteAssessmentStore } from "@/store/assessmentStore";

// Types
import { DynamicMCQQuestion, MCQQuestion, HandWrittenQuestion, AIGeneratedMCQQuestion } from "@/types/assessment.type";


export function useAssessmentQuery() {
    const router = useRouter();


    const { assessmentId } = useParams();
    const useAssessmentStore = createAssessmentStore(assessmentId as string);
    const { questions, sections } = useAssessmentStore();


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
        mutationFn: ({ question, assessmentId }: { question: MCQQuestion, assessmentId: string }) => mcqQuestion({ question, assessmentId, sections }),
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
    const { mutate: createHandwrittenQuestionMutation, isPending: isCreatingHandwrittenQuestion, } = useMutation({
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
        return isCreatingDynamicMcqQuestion || isCreatingMcqQuestion || isCreatingHandwrittenQuestion || isCreatingAIGeneratedMcqQuestion;
    }, [isCreatingDynamicMcqQuestion, isCreatingMcqQuestion, isCreatingHandwrittenQuestion, isCreatingAIGeneratedMcqQuestion])

    const handleCreateAssessment = async () => {
        if (!assessmentId && typeof assessmentId !== "string") {
            toast.error("Invalid Assessment ID");
            return;
        }

        // Create an array to store all mutation promises
        const mutationPromises = questions.map((question) => {
            return new Promise((resolve, reject) => {
                switch (question.questionType) {
                    case "dynamicMcq":
                        createDynamicMcqQuestionMutation(
                            { question, assessmentId: assessmentId as string, sections },
                            {
                                onError: () => {
                                    reject();
                                },
                                onSuccess: () => {
                                    resolve(true);
                                }
                            }
                        );
                        break;
                    case "handWritten":
                        createHandwrittenQuestionMutation(
                            { question, assessmentId: assessmentId as string },
                            {
                                onError: () => {
                                    reject();
                                },
                                onSuccess: () => {
                                    resolve(true);
                                }
                            }
                        );
                        break;
                    case "mcq":
                        createMcqQuestionMutation(
                            { question, assessmentId: assessmentId as string },
                            {
                                onError: () => {
                                    reject();
                                },
                                onSuccess: () => {
                                    resolve(true);
                                }
                            }
                        );
                        break;
                    case "aiMcq":
                        createAIGeneratedMcqQuestionMutation(
                            { question, assessmentId: assessmentId as string, sections },
                            {
                                onError: () => {
                                    reject();
                                },
                                onSuccess: () => {
                                    resolve(true);
                                }
                            }
                        );
                        break;
                    default:
                        toast.error("Unknown question type");
                        reject();
                }
            });
        });

        // Wait for all mutations to complete
        try {
            await Promise.all(mutationPromises);
            // toast.success("All questions created successfully");
            router.back();
            deleteAssessmentStore(assessmentId as string);
        } catch {
            // toast.error("Failed to create some questions");
        }
    }


    return { handleCreateAssessment, isCreating }
}
