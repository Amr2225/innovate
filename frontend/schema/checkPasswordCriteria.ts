import { z } from "zod";

export const checkPasswordCriteria = (password: string, ctx: z.RefinementCtx) => {
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
}