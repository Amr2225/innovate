"use client";

import { Bar, BarChart, CartesianGrid, LabelList, XAxis, YAxis } from "recharts";

import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

export const description = "A bar chart with a custom label";

export function CustomBarChart<T>({
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
      <BarChart
        accessibilityLayer
        data={chartData}
        layout='vertical'
        margin={{
          right: 16,
        }}
      >
        <CartesianGrid horizontal={false} />
        <YAxis
          dataKey={dataKeyY}
          type='category'
          tickLine={false}
          tickMargin={10}
          axisLine={false}
          // tickFormatter={(value) => value.slice(0, 3)}
          hide
        />
        <XAxis dataKey={dataKeyX} type='number' hide />
        <ChartTooltip cursor={false} content={<ChartTooltipContent indicator='line' />} />
        <Bar dataKey={dataKeyX} layout='vertical' fill='hsl(var(--primary))' radius={4}>
          <LabelList
            dataKey={dataKeyY}
            position='insideLeft'
            offset={8}
            className='fill-white'
            fontSize={12}
          />
          <LabelList
            dataKey={dataKeyX}
            position='right'
            offset={8}
            className='fill-foreground'
            fontSize={12}
          />
        </Bar>
      </BarChart>
    </ChartContainer>
  );
}
