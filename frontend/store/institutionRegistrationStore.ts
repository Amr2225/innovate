import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { EncryptedStorage } from './encryptedStorage'
import { FileData } from '@/types/file.type'


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
    hmac: string | null
    reset: () => void
    setFile: (file: File) => void
    getFile: () => Promise<File | null>
    setCredits: (credits: number) => void
    addCreds: (name: string, email: string, password: string, confirm_password: string) => void
    setCurrentStep: () => void
    setStatus: (key: keyof Pick<InstitutionStore, 'isRegistrationSuccess' | 'isEmailVerified' | 'isPaymentSuccess'>, value: boolean) => void
    goBack: () => void
    setHmac: (hmac: string) => void
    verficationFailedCallback: () => void
}

const initialState: Pick<InstitutionStore, 'name' | 'email' | 'password' | 'confirm_password' | 'isEmailVerified' | 'isPaymentSuccess' | 'isRegistrationSuccess' | 'current_step' | 'credits' | 'logoData' | 'hmac'> = {
    name: '',
    email: '',
    password: '',
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
            setFile: async (file: File) => {
                const arrayBuffer = await file.arrayBuffer();
                // Convert ArrayBuffer to Base64 string for storage
                const base64String = btoa(
                    String.fromCharCode(...new Uint8Array(arrayBuffer))
                );
                set({
                    logoData: {
                        name: file.name,
                        type: file.type,
                        size: file.size,
                        lastModified: file.lastModified,
                        arrayBuffer: base64String
                    }
                });
            },
            getFile: async () => {
                const logoData = get().logoData;
                if (!logoData) return null;

                // Convert Base64 string back to ArrayBuffer
                const binaryString = atob(logoData.arrayBuffer as string);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }

                const file = new File(
                    [bytes],
                    logoData.name,
                    {
                        type: logoData.type,
                        lastModified: logoData.lastModified
                    }
                );

                return file;
            },
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
