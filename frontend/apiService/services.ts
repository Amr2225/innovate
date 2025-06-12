// Verification Services
import {
    institutionVerifyEmail,
    institutionSendVerificationEmail,
    institutionVerifyEmailExists,
    verifyEmailToken,
    verifyEmail,
    resendEmail,
    IVerifyEmail
} from "./verificationService";

// Institution Services
import { bulkUserInsert, getMembers, generatePaymentLink, updateUser, deleteUser, registerSingleUser } from "./institutionService";

export const institutionVerificationService: IVerifyEmail = {
    resendVerificationEmail: institutionSendVerificationEmail,
    verifyEmailExists: institutionVerifyEmailExists,
    verifyEmail: institutionVerifyEmail,
}

export const userVerificationService: IVerifyEmail = {
    resendVerificationEmail: resendEmail,
    verifyEmailExists: verifyEmailToken,
    verifyEmail: verifyEmail,
}

// Institution Services
export const institutionService = {
    getMembers,
    bulkUserInsert,
    updateUser,
    deleteUser,
    registerSingleUser,
}

export const paymentService = {
    generatePaymentLink,
}
