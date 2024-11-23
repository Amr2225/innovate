import z from "zod";

export const LoginSchema = z.object({
    email: z.string({ required_error: "String is required" }).email({ message: "Invalid Email" }),
    password: z.string({ required_error: "Password is required" }).min(8, { message: "Password must be 8 Characters long" })
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

})

export type LoginSchemaType = z.infer<typeof LoginSchema>