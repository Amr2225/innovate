'use server'

import { z } from 'zod'
import { revalidatePath } from 'next/cache'
import { api } from '@/apiService/api'

// Validation schema
const changePasswordSchema = z.object({
    oldPassword: z.string().min(1, 'Old password is required'),
    newPassword: z
        .string()
        .min(8, 'Password must be at least 8 characters')
        .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
        .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
        .regex(/[0-9]/, 'Password must contain at least one number')
        .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),
    confirmPassword: z.string().min(1, 'Confirm password is required'),
}).refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
})

export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>

export async function changePassword(formData: ChangePasswordFormData) {
    try {
        // Validate input data
        const validatedData = changePasswordSchema.parse(formData)

        // Make API request to change password
        const response = await api.put(`/auth/user/change-password/`, {
            old_password: validatedData.oldPassword,
            new_password: validatedData.newPassword,
            confirm_password: validatedData.confirmPassword,
        })

        if (response.status !== 200) {
            return {
                success: false,
                message: response.data.detail || 'Failed to change password',
            }
        }

        // Revalidate any cached data
        revalidatePath('/student/settings')

        return {
            success: true,
            message: 'Password updated successfully',
        }
    } catch (error) {
        if (error instanceof z.ZodError) {
            return {
                success: false,
                errors: error.errors.reduce((acc, curr) => {
                    const field = curr.path[0] as string
                    acc[field] = curr.message
                    return acc
                }, {} as Record<string, string>),
            }
        }

        return {
            success: false,
            message: error instanceof Error ? error.message : 'Something went wrong',
        }
    }
}
