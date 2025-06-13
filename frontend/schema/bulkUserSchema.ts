import * as z from "zod";

export const BulkUserSchema = z.object({
    excelFile: z
        .instanceof(File, { message: "Excel file is required" })
        .refine((file) => file.size > 0, "Please select a file")
        .refine(
            (file) =>
                file.type === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
                file.type === "application/vnd.ms-excel" ||
                file.type === "text/csv",
            "Please upload an Excel file (.xlsx or .xls or .csv)"
        ),
});

export type BulkUserSchemaType = z.infer<typeof BulkUserSchema>;