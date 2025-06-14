import { z } from "zod";

export const OTPSchema = z.object({
    pin: z.string().min(6, {
        message: "Your one-time password must be 6 characters.",
    }),
});

export type OTPSchemaType = z.infer<typeof OTPSchema>;
