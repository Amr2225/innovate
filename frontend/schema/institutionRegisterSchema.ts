import { z } from "zod";
import { BaseRegisterSchema } from "./registerSchema";
import { checkPasswordCriteria } from "@/schema/checkPasswordCriteria";

const MAX_FILE_SIZE = 5000000;
const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png"];
export const InstitutionRegisterSchema = BaseRegisterSchema.pick({
    email: true,
    password: true,
    confirm_password: true,
}).extend({
    name: z.string().min(1, { message: "Name is required" }),
    logo: z
        .instanceof(File, { message: "Logo is required" })
        .nullable()
        .refine((file) => {
            if (!file) return true;
            return file.size <= MAX_FILE_SIZE && ACCEPTED_IMAGE_TYPES.includes(file.type);
        }, "Max image size is 5MB.")
        .refine(
            (file) => {
                if (!file) return true;
                return ACCEPTED_IMAGE_TYPES.includes(file?.type);
            },
            "Only .jpg, .jpeg, and .png formats are supported."
        )
}).superRefine(({ password }, ctx) => {
    checkPasswordCriteria(password, ctx)
}).refine((data) => data.password === data.confirm_password, {
    message: "Passwords don't match",
    path: ["confirm_password"], // path of error
});

export type InstitutionRegisterSchemaType = z.infer<typeof InstitutionRegisterSchema>
