import { api } from "./api";
import { UserUpdate } from "@/types/user.types";

export const getUserProfileData = async (): Promise<UserUpdate> => {
    const response = await api.get("auth/user/update/");

    if (response.status === 200) return response.data as UserUpdate
    throw new Error("Failed to fetch user profile data");
};

export const updateUserProfileData = async (data: UserUpdate) => {
    const response = await api.put("auth/user/update/", data);

    if (response.status === 200) return response.data as UserUpdate
    throw new Error("Failed to update user profile data");
};
