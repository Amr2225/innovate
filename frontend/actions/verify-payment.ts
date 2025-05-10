"use server"

import axios from "axios";

export const verifyPayment = async (hmac: string, data: unknown): Promise<boolean> => {
    const res = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/institution/payment/verify/`, { hmac, data },
        {
            validateStatus: status => status < 500
        }
    );
    return res.status === 201;
};
