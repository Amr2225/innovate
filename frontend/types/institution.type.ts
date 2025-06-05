export type PricePlans = "Silver" | "Gold" | "Diamond";

export interface Plan {
    id: string;
    description: description[];
    currency: string;
    type: PricePlans;
    students_limit: number;
    credit_price: string
    minimum_credits: number
}

type description = {
    text: string
    isAdvantage: boolean
}