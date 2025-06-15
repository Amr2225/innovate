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

export interface InstitutionPolicy {
    id: string;
    min_passing_percentage: number;
    max_allowed_failures: number;
    min_gpa_required: number;
    min_attendance_percent: number;
    max_allowed_courses_per_semester: number;
    year_registration_open: boolean;
    summer_registration_open: boolean;
    // promotion_time: Date;
    access_code: string;
}