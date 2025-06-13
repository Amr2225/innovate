import { z } from "zod";

export const courseSchema = z.object({
    name: z.string().min(1, "Course name is required"),
    description: z.string().min(1, "Description is required"),
    prerequisite_course: z.string().nullable(),
    instructors: z.array(z.string()).min(1, "At least one instructor is required"),
    semester: z.number({ message: "Semester is required" }).min(1, "Semester must be at least 1"),
    credit_hours: z
        .number({ message: "Credit hours is required" })
        .min(1, "Credit hours must be at least 1"),
    total_grade: z
        .number({ message: "Total grade is required" })
        .min(1, "Total grade must be at least 1"),
});

export type CourseSchema = z.infer<typeof courseSchema>;
