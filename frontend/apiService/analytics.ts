import { api } from "./api";


interface StudentPerCourse {
    courses: {
        course_name: string;
        active_students: number;
    }[];
    overall_statistics: {
        total_courses: number;
        total_active_students: number;
    }
}

interface CourseAvgScore {
    courses: {
        course_name: string;
        avg_score: number;
        assessment_metrics: {
            average_score: number;
        }
    }[];
    overall_metrics: {
        total_courses: number;
        total_students: number;
        average_completion_rate: number;
        average_assessment_score: number;
    }
}

interface TopStudents {
    course_id: string;
    course_name: string;
    top_students: {
        student_id: string;
        student_name: string;
        total_grade: number;
    }[];
}

export const getTeacherCourseStudentAnalytics = async (): Promise<StudentPerCourse> => {
    const response = await api.get('/api/teacher-analytics/');

    if (response.status === 200) return response.data;
    throw new Error(response.data.message || "Something went wrong");
}

export const getCourseAvgScore = async (): Promise<CourseAvgScore> => {
    const response = await api.get('/api/teacher-analytics/courses-metrics');

    if (response.status === 200) return response.data;
    throw new Error(response.data.message || "Something went wrong");
}


export const getTopStudents = async ({ courseId }: { courseId: string }): Promise<TopStudents> => {
    const response = await api.get(`/api/teacher-analytics/top-students/${courseId}`);

    if (response.status === 200) return response.data;
    throw new Error(response.data.message || "Something went wrong");
}
