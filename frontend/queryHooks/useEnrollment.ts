import { enrollInCourse, getEligibleCourses } from "@/apiService/enrollmentService";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export function useEnrollment() {
    const queryClient = useQueryClient()
    const { data: availableCourses, isLoading, error } = useQuery({
        queryKey: ["avaibleCourses"],
        queryFn: getEligibleCourses
    })

    const { mutate: enroll, isPending: isEnrolling } = useMutation({
        mutationFn: (courseId: string) => enrollInCourse(courseId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["avaibleCourses"] })
            toast.success("Enrolled in course")
        },
        onError: (error) => {
            // console.error(error)
            toast.error(error.message)
        }
    })

    return { availableCourses, isLoading, error, enroll, isEnrolling }
}