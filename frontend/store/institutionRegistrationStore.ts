import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { EncryptedStorage } from './encryptedStorage'

type FileData = {
    name: string;
    type: string;
    size: number;
    lastModified: number;
    arrayBuffer: string;
}

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
    logo: File | null
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

const initialState: InstitutionStore = {
    name: '',
    email: '',
    password: '',
    confirm_password: '',
    isEmailVerified: false,
    isPaymentSuccess: false,
    isRegistrationSuccess: false,
    current_step: 1,
    credits: 0,
    logo: null,
    logoData: null,
    hmac: null,
    setHmac: () => { },
    reset: () => { },
    setStatus: () => { },
    setCredits: () => { },
    addCreds: () => { },
    setCurrentStep: () => { },
    goBack: () => { },
    verficationFailedCallback: () => { },
    setFile: () => { },
    getFile: () => Promise.resolve(null)
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
                console.log("Setting file", file);
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
                set({
                    name: initialState.name,
                    email: initialState.email,
                    password: initialState.password,
                    confirm_password: initialState.confirm_password,
                    isEmailVerified: initialState.isEmailVerified,
                    isPaymentSuccess: initialState.isPaymentSuccess,
                    isRegistrationSuccess: initialState.isRegistrationSuccess,
                    current_step: initialState.current_step,
                    credits: initialState.credits,
                    logo: initialState.logo,
                    hmac: initialState.hmac
                });
                get().setCurrentStep();
            },
            setStatus: (key, value) => {
                set({ [key]: value });
                get().setCurrentStep();
            },
            setCurrentStep: () => {
                console.log("isEmailVerified", get().isEmailVerified);
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