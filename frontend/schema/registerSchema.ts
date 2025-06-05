import { checkPasswordCriteria } from "@/schema/checkPasswordCriteria";
import { z } from "zod";

export const BaseRegisterSchema = z.object({
    first_name: z.string().min(1, { message: "First name is required" }),
    middle_name: z.string().min(1, { message: "Middle name is required" }),
    last_name: z.string().min(1, { message: "Last name is required" }),
    email: z.string({ required_error: "Email is required" }).email({ message: "Email is required" }),
    birth_date: z.date({ required_error: "Birth Date is required" }),
    password: z.string({ required_error: "Password is required" }).min(8, { message: "Password must be 8 Characters long" }),
    confirm_password: z.string(),
})


export const RegisterSchema = BaseRegisterSchema
    .superRefine(({ password }, ctx) => {
        checkPasswordCriteria(password, ctx)
    }).refine((data) => data.password === data.confirm_password, {
        message: "Passwords don't match",
        path: ["confirm_password"], // path of error
    });




export type RegisterSchemaType = z.infer<typeof RegisterSchema>