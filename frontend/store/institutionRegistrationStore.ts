import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { EncryptedStorage } from './encryptedStorage'
import { FileData } from '@/types/file.type'
import { getImageMetadata, ImageMetadata, saveImage } from './imageStorage'


type InstitutionStore = {
    name: string
    email: string
    password: string
    confirm_password: string
    is_verified: boolean
    is_payment_success: boolean
    current_step: number
    credits: number
    logoData: FileData | null
    logoStorageKey: string
    hmac: string | null
    reset: () => void
    setLogo: (Logo: File) => Promise<void>
    // getFile: () => Promise<File | null>
    getLogoName: () => Promise<ImageMetadata | null>
    setCredits: (credits: number) => void
    addCreds: (name: string, email: string, password: string, confirm_password: string) => void
    setIsVerified: () => void
    setCurrentStep: () => void
    goBack: () => void
    verifcationFaildCallback: () => void
=========
    signIn: (name: string, email: string) => void
    logo?: string
>>>>>>>>> Temporary merge branch 2
}

const initialState: Pick<InstitutionStore, 'name' | 'email' | 'password' | 'confirm_password' | 'isEmailVerified' | 'isPaymentSuccess' | 'isRegistrationSuccess' | 'current_step' | 'credits' | 'logoData' | 'hmac' | "logoStorageKey"> = {
    name: '',
    email: '',
<<<<<<<<< Temporary merge branch 1
    password: '',
    logoStorageKey: '',
    confirm_password: '',
    is_verified: false,
    is_payment_success: false,
    current_step: 1,
    credits: 0,
    reset: () => { },
    setIsPaymentSuccess: () => { },
    addCreds: () => { },
    setIsVerified: () => { },
    setCurrentStep: () => { },
    goBack: () => { },
    verifcationFaildCallback: () => { }
}


export const useInstitutionRegistrationStore = create<InstitutionStore>()(
    persist(
        (set, get) => ({
            ...initialState,
            addCreds: (name, email, password, confirm_password) => {
                set({ name, email, password, confirm_password });
                get().setCurrentStep();
            },
            setLogo: async (Logo: File) => {
                const imageKey = `image_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
                await saveImage(Logo, imageKey)
                set({
                    logoData: {
                        name: Logo.name,
                        lastModified: Logo.lastModified,
                        size: Logo.size,
                        type: Logo.type
                    },
                    logoStorageKey: imageKey
                })
            },
            getLogoName: async () => {
                return await getImageMetadata("123")
            },
            // getFile: async () => {

            // },
            setHmac: (hmac: string) => {
                set({ hmac });
            },
            setCredits: (credits: number) => {
                set({ credits });
            },
            reset: () => {
                set(initialState);
            },
            setIsVerified: () => {
                set({ is_verified: true });
                get().setCurrentStep();
            },
            setCurrentStep: () => {
                if (get().name && !get().is_verified) set({ current_step: 2 })
                if (get().is_verified) set({ current_step: 3 })
                if (get().is_payment_success) set({ current_step: 4 })
            },
            goBack: () => {
                if (get().current_step === 1 || get().is_verified) return;
                set({ current_step: get().current_step - 1 })
            },
            verifcationFaildCallback: () => set({ current_step: 1 })
        }),
        {
            name: 'institution-registration',
            storage: createJSONStorage(() => new EncryptedStorage()),
        },
    ),
)

// Run setCurrentStep on initialization
useInstitutionRegistrationStore.getState().setCurrentStep();
