import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { EncryptedStorage } from './encryptedStorage'

type InstitutionStore = {
    name: string
    email: string
    password: string
    confirm_password: string
    is_verified: boolean
    is_payment_success: boolean
    current_step: number
    credits: number
    logo?: string
    addCreds: (name: string, email: string, password: string, confirm_password: string) => void
    setIsVerified: () => void
    setCurrentStep: () => void
    goBack: () => void
    verifcationFaildCallback: () => void
}

const initialState: InstitutionStore = {
    name: '',
    email: '',
    password: '',
    confirm_password: '',
    is_verified: false,
    is_payment_success: false,
    current_step: 1,
    credits: 0,
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
            setIsVerified: () => {
                set({ is_verified: true });
                get().setCurrentStep();
            },
            setCurrentStep: () => {
                if (get().name && !get().is_verified) set({ current_step: 2 })
                if (get().is_verified) set({ current_step: 3 })
                if (get().credits > 0) set({ current_step: 4 })
            },
            goBack: () => {
                if (get().current_step === 1 || get().is_verified) return;// 
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