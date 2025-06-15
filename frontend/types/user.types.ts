export type Role = "Student" | "Teacher" | "Institution";

export interface User {
    id?: string
    name: string
    email: string
    role: Role
    credits?: number | undefined
    profile_picture?: string
}

export interface NewUser {
    national_id: string
}

export interface UserUpdate {
    first_name?: string
    middle_name?: string
    last_name?: string
    email?: string
    birth_date?: Date
    age?: number
    avatar?: string
    logo?: string
    name?: string
}


export interface InstitutionMembersType {
    id: string;
    first_name: string;
    middle_name: string;
    last_name: string;
    full_name: string;
    email: string;
    role: string;
    institution: string;
    national_id: string;
    birth_date: string;
    age: number;
    date_joined: string;
    is_email_verified: boolean;
    is_active: boolean;
}


export interface SubmissionData extends Omit<InstitutionMembersType, 'is_email_verified' | 'is_active' | "first_name" | "middle_name" | "last_name" | "date_joined"> {
    name: string;
    error?: string;
}


export interface UserResponse {
    first_name: string;
    middle_name: string;
    last_name: string;
    email: string;
    role: string;
    national_id: string;
    birth_date: string;
    age: number;
}

export interface BulkInsertResponse {
    success: boolean;
    created_users: UserResponse[];
    errors: {
        row: UserResponse;
        errors: {
            [key: string]: string[];
        };
    }[];
}

// Subset without personal details
export interface InstitutionMemberBasic extends Omit<InstitutionMembersType,
    'first_name' | 'middle_name' | 'last_name' | 'birth_date' | 'age' | 'is_email_verified'> {
    name: string; // Combined name field
}

// Subset with only essential info
export interface InstitutionMemberMinimal extends Pick<InstitutionMembersType,
    'email' | 'role' | 'institution' | 'national_id'> {
    name: string;
}

export interface InstitutionMemberWithCourses extends InstitutionMembersType {
    courses: {
        id: string;
        title: string;
        progress: number;
        last_accessed: string;
        status: 'enrolled' | 'completed' | 'dropped';
    }[];
    total_courses: number;
    completed_courses: number;
    average_progress: number;
}
