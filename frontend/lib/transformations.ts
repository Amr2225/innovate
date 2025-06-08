import { BulkInsertResponse, SubmissionData } from "@/types/user.types";
import moment from "moment";

export const transformData = (data: BulkInsertResponse, institution: string): SubmissionData[] => {
    const transformedData: SubmissionData[] = [];

    data.errors.forEach((record) => {
        transformedData.push({
            name: record.row.first_name + " " + record.row.middle_name + " " + record.row.last_name,
            email: record.row.email ?? "-",
            role: record.row.role,
            institution: institution,
            national_id: record.row.national_id,
            birth_date: moment(record.row.birth_date).format("YYYY-MM-DD"),
            age: record.row.age,
            error: Object.values(record.errors)[0][0],
        });
    });

    data.created_users.forEach((record) => {
        transformedData.push({
            name: record.first_name + " " + record.middle_name + " " + record.last_name,
            email: record.email,
            role: record.role,
            institution: institution,
            national_id: record.national_id,
            birth_date: moment(record.birth_date).format("YYYY-MM-DD"),
            age: record.age,
        });
    });

    return transformedData;
};