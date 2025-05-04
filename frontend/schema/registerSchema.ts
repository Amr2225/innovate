import z from "zod";

export const RegisterSchema = z.object({
    first_name: z.string().min(1, { message: "First name is required" }),
    middle_name: z.string().min(1, { message: "Middle name is required" }),
    last_name: z.string().min(1, { message: "Last name is required" }),
    email: z.string({ required_error: "String is required" }).email({ message: "Invalid Email" }),
    birth_date: z.date({ required_error: "Birth Date is required" }),
    password: z.string({ required_error: "Password is required" }).min(8, { message: "Password must be 8 Characters long" }),
    confirm_password: z.string(),
}).superRefine(({ password }, ctx) => {
    const checkUppercase = (ch: string) => /[A-Z]/.test(ch);
    const checkLowercase = (ch: string) => /[a-z]/.test(ch);
    const checkSpeicalChar = (ch: string) => /[`!@#$%^&*()_\-+=\[\]{};':"\\|,.<>\/?~ ]/.test(ch);

    let containsUpperCase = false,
        containsLowerCase = false,
        containsSpeicalChar = false,
        containsNumber = false

    for (const char of password) {
        if (!containsNumber && !isNaN(+char)) containsNumber = true;
        else if (!containsLowerCase && checkLowercase(char)) containsLowerCase = true
        else if (!containsUpperCase && checkUppercase(char)) containsUpperCase = true;
        else if (!containsSpeicalChar && checkSpeicalChar(char)) containsSpeicalChar = true
    }

    if (!containsNumber || !containsLowerCase || !containsUpperCase || !containsSpeicalChar) {
        ctx.addIssue({
            code: "custom",
            path: ["password"],
            message: "Password must contain a number, lower, upper case, and a special character"
        })
    }

}).refine((data) => data.password === data.confirm_password, {
    message: "Passwords don't match",
    path: ["confirm_password"], // path of error
});

export type RegisterSchemaType = z.infer<typeof RegisterSchema>