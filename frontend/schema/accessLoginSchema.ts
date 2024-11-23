import { z } from "zod"

export const accessLoginSchema = z.object({
    // Access code might not be a number after implementing the backend
    accessCode: z.string().min(5, { message: "Invalid access code" }).refine((val) => !isNaN(Number(val)), { message: "Access code must be a number" }),
    naitonal: z.string().min(14, {
        message: "Invalid National ID"
    }).max(14, {
        message: "Invalid National ID"
    }).refine((val) => !isNaN(Number(val)), { message: "National ID must be a number" })
})

export type AccessLoginSchemaType = z.infer<typeof accessLoginSchema>