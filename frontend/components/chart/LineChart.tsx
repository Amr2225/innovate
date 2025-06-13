import React from "react";

import { CartesianGrid, Line, LineChart, YAxis } from "recharts";

import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

export default function CustomnLineChart<T>({
  chartConfig,
  dataKeyY,
  dataKeyX,
  chartData,
}: {
  chartConfig: ChartConfig;
  dataKeyY: string;
  dataKeyX: string;
  chartData: T[];
}) {
  return (
    <ChartContainer config={chartConfig}>
      <LineChart
        accessibilityLayer
        data={chartData}
        margin={{
          top: 24,
          //   left: 24,
          right: 24,
          bottom: 50,
        }}
      >
        <CartesianGrid vertical={false} />
        <YAxis dataKey={dataKeyY} tickLine={false} axisLine={false} tickMargin={10} />
        <ChartTooltip
          cursor={true}
          content={
            <ChartTooltipContent
              className='w-[200px]'
              indicator='line'
              nameKey={dataKeyY}
              hideLabel
            />
          }
        />
        <Line
          dataKey={dataKeyY}
          type='natural'
          stroke='hsl(var(--primary))'
          strokeWidth={2}
          dot={{
            fill: "hsl(var(--primary))",
          }}
          activeDot={{
            r: 6,
          }}
        />

        <Line
          dataKey={dataKeyX}
          type='natural'
          stroke='hsl(var(--primary))'
          strokeWidth={2}
          dot={{
            fill: "hsl(var(--primary))",
          }}
          activeDot={{
            r: 6,
          }}
        />
      </LineChart>
    </ChartContainer>
  );
}
