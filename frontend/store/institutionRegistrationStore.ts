import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

type InstitutionStore = {
    name: string
    email: string
    signIn: (name: string, email: string) => void
    logo?: string
}

const initialState: InstitutionStore = {
    name: '',
    email: '',
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