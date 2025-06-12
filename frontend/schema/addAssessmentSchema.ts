import { z } from "zod";

export const addAssessmentSchema = z.object({
    title: z.string().min(1, "Title is required"),
    course: z.string().min(1, "Course is required"),
    type: z.enum(["Assignment", "Exam", "Quiz"], {
        required_error: "Type is required",
        invalid_type_error: "Type must be either Assignment, Exam, or Quiz",
    }),
    start_date: z.date().nullable(),
    due_date: z.date(),
    total_grade: z
        .number({ message: "Total grade is required" })
        .min(1, "Total grade must be at least 1"),
});

export type AddAssessmentSchema = z.infer<typeof addAssessmentSchema>;
