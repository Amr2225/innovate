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
    isEmailVerified: boolean
    isPaymentSuccess: boolean
    isRegistrationSuccess: boolean
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
    setCurrentStep: () => void
    setStatus: (key: keyof Pick<InstitutionStore, 'isRegistrationSuccess' | 'isEmailVerified' | 'isPaymentSuccess'>, value: boolean) => void
    goBack: () => void
    setHmac: (hmac: string) => void
    verficationFailedCallback: () => void
}

const initialState: Pick<InstitutionStore, 'name' | 'email' | 'password' | 'confirm_password' | 'isEmailVerified' | 'isPaymentSuccess' | 'isRegistrationSuccess' | 'current_step' | 'credits' | 'logoData' | 'hmac' | "logoStorageKey"> = {
    name: '',
    email: '',
    password: '',
    logoStorageKey: '',
    confirm_password: '',
    isEmailVerified: false,
    isPaymentSuccess: false,
    isRegistrationSuccess: false,
    current_step: 1,
    credits: 0,
    logoData: null,
    hmac: null,
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
                set({ ...initialState });
                get().setCurrentStep();
            },
            setStatus: (key, value) => {
                set({ [key]: value });
                get().setCurrentStep();
            },
            setCurrentStep: () => {
                if (get().name && get().email && !get().isEmailVerified) set({ current_step: 2 })
                if (get().isEmailVerified) set({ current_step: 3 })
                if (get().credits > 0 && get().isEmailVerified) set({ current_step: 4 })
            },
            goBack: () => {
                if (get().current_step === 1) return;
                if (get().isEmailVerified) return get().reset();
                set({ current_step: get().current_step - 1 })
            },
            verficationFailedCallback: () => set({ current_step: 1 })
        }),
        {
            name: 'institution-registration',
            storage: createJSONStorage(() => new EncryptedStorage()),
        },
    ),
)

// Run setCurrentStep on initialization
useInstitutionRegistrationStore.getState().setCurrentStep();
