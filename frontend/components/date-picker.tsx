"use client";
// import { format } from "date-fns";
import moment from "moment";
import { CalendarIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

interface DatePickerProps {
  date?: Date;
  setDate?: (...event: unknown[]) => void;
}
export default function DatePicker({ date, setDate }: DatePickerProps) {
  return (
    <div className='w-full'>
      <Popover>
        <PopoverTrigger asChild>
          <Button
            variant={"outline"}
            className={cn(
              "w-full justify-start text-left font-normal",
              !date && "text-muted-foreground"
            )}
          >
            <CalendarIcon />
            {date ? moment(date).format("DD/MM/YYYY") : <span>Pick a date</span>}
          </Button>
        </PopoverTrigger>
        <PopoverContent className='w-auto p-0' align='start'>
          <Calendar mode='single' selected={date} onSelect={setDate} initialFocus />
        </PopoverContent>
      </Popover>
    </div>
  );
}

export function BirthDatePicker({ date, setDate }: DatePickerProps) {
  return (
    <div className='w-full'>
      <Popover>
        <PopoverTrigger asChild>
          <Button
            variant={"outline"}
            className={cn(
              "w-full justify-start text-left font-normal",
              !date && "text-muted-foreground"
            )}
          >
            <CalendarIcon />
            {date ? moment(date).format("DD/MM/YYYY") : <span>Pick a date</span>}
          </Button>
        </PopoverTrigger>
        <PopoverContent className='w-auto p-0' align='start'>
          <Calendar
            selected={date}
            onSelect={setDate}
            mode='single'
            // disabled={(date) => date > new Date() || date < new Date("1900-01-01")}
            captionLayout='dropdown'
            toYear={2200}
            fromYear={1940}
            classNames={{
              day_hidden: "invisible",
              dropdown:
                "px-2 py-1.5 rounded-md bg-popover text-popover-foreground text-sm  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ring-offset-background",
              caption_dropdowns: "flex gap-3",
              vhidden: "hidden",
              caption_label: "hidden",
            }}
          />
        </PopoverContent>
      </Popover>
    </div>
  );
}
