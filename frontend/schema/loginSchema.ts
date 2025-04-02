import z from "zod";

export const LoginSchema = z.object({
    email: z.string({ required_error: "String is required" }).email({ message: "Invalid Email" }),
    password: z.string({ required_error: "Password is required" }).min(1, { message: "Password is required" })
})

export type LoginSchemaType = z.infer<typeof LoginSchema>