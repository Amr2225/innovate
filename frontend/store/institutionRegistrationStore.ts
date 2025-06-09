import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
<<<<<<< HEAD
import { EncryptedStorage } from './encryptedStorage'
import { FileData } from '@/types/file.type'

=======
>>>>>>> sherif

type InstitutionStore = {
    name: string
    email: string
<<<<<<<<< Temporary merge branch 1
    password: string
    confirm_password: string
    is_verified: boolean
    is_payment_success: boolean
    current_step: number
    credits: number
    logo?: string
    reset: () => void
    setIsPaymentSuccess: (isVerified: boolean) => void
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

const initialState: Pick<InstitutionStore, 'name' | 'email' | 'password' | 'confirm_password' | 'isEmailVerified' | 'isPaymentSuccess' | 'isRegistrationSuccess' | 'current_step' | 'credits' | 'logoData' | 'hmac'> = {
    name: '',
    email: '',
<<<<<<<<< Temporary merge branch 1
    password: '',
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
            setIsPaymentSuccess: (isVerified: boolean) => {
                set({ is_payment_success: isVerified });
                get().setCurrentStep();
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
=========
    signIn: () => { },
}

export const useBearStore = create<InstitutionStore>()(
    persist(
        (set) => ({
            ...initialState,
            signIn: (name, email) => set({ name: name, email: email }),
        }),
        {
            name: 'institution-registration', // name of the item in the storage (must be unique)
            storage: createJSONStorage(() => localStorage), // (optional) by default, 'localStorage' is used
        },
    ),
)
>>>>>>>>> Temporary merge branch 2
