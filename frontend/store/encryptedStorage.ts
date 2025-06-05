import { PersistStorage } from "zustand/middleware";
import CryptoJS from "crypto-js";

const SECRET_KEY = process.env.NEXT_PUBLIC_STORE_ENCRYPTION_KEY!;

type StorageValue = string | number | boolean | object | null;
export class EncryptedStorage implements PersistStorage<unknown> {
    getItem(key: string) {
        const value = localStorage.getItem(key);

        if (value) {
            const decryptedBytes = CryptoJS.AES.decrypt(value, SECRET_KEY)
            const decryptedValue = decryptedBytes.toString(CryptoJS.enc.Utf8);
            return JSON.parse(decryptedValue);
        }

        return null;
    }

    setItem(key: string, value: StorageValue): void {
        const encrypted = CryptoJS.AES.encrypt(JSON.stringify(value), SECRET_KEY).toString()
        localStorage.setItem(key, encrypted);
    }

    removeItem(key: string): void {
        localStorage.removeItem(key);
    }
}