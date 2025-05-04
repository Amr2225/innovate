import { z } from "zod"

export const loginAccessSchema = z.object({
    // Access code might not be a number after implementing the backend
    accessCode: z.string().min(8, { message: "Invalid access code" }),
    nationalId: z.string().length(14, {
        message: "Invalid National ID"
    }).refine((val) => !isNaN(Number(val)), { message: "National ID must be a number" })
})

export type LoginAccessSchemaType = z.infer<typeof loginAccessSchema>