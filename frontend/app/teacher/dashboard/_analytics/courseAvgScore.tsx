"use client";
import CustomnLineChart from "@/components/chart/LineChart";
import { useQuery } from "@tanstack/react-query";
import { getCourseAvgScore } from "@/apiService/analytics";
import Loader from "@/components/Loader";
import { useMemo } from "react";
import { ChartConfig } from "@/components/ui/chart";

interface ReshapedData {
  course: string;
  avgScore: number;
}

export default function CourseAvgScore() {
  const { data, isLoading } = useQuery({
    queryKey: ["course-avg-score"],
    queryFn: () => getCourseAvgScore(),
    select: (data) =>
      data.courses.map((item) => ({
        course: item.course_name,
        avgScore: item.assessment_metrics.average_score,
      })),
  });
  const reshapedData = useMemo(() => data as ReshapedData[], [data]);

  const chartConfig = useMemo(() => {
    if (isLoading) return null;
    return reshapedData.reduce(
      (acc, item) => ({
        ...acc,
        [item.course]: {
          label: item.course,
        },
      }),
      {}
    );
  }, [reshapedData, isLoading]);

  if (isLoading) return <Loader />;

  return (
    <CustomnLineChart
      chartConfig={chartConfig as ChartConfig}
      dataKeyY='avgScore'
      dataKeyX='course'
      chartData={data || []}
    />
  );
}
