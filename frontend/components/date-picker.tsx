"use client";
// import { format } from "date-fns";
import moment from "moment";
import { CalendarIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useState } from "react";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";

interface DatePickerProps {
  date?: Date;
  setDate?: (...event: unknown[]) => void;
  saveButton?: React.ReactNode;
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

export function BirthDatePicker({ date, setDate, saveButton }: DatePickerProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleOpenChange = (newOpenState: boolean) => {
    setIsOpen(newOpenState);
    setTimeout(() => {
      document.body.style.pointerEvents = "";
    }, 100);
  };

  return (
    <div className='w-full'>
      <Popover open={isOpen} onOpenChange={handleOpenChange}>
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
            defaultMonth={date}
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
          {saveButton && saveButton}
        </PopoverContent>
      </Popover>
    </div>
  );
}

export function DateTimePicker({ date, setDate }: DatePickerProps) {
  const hours = Array.from({ length: 12 }, (_, i) => i + 1);

  const handleDateSelect = (selectedDate: Date | undefined) => {
    if (selectedDate) {
      setDate?.(selectedDate);
    }
  };

  const handleTimeChange = (type: "hour" | "minute" | "ampm", value: string) => {
    if (date) {
      const newDate = new Date(date);
      if (type === "hour") {
        newDate.setHours((parseInt(value) % 12) + (newDate.getHours() >= 12 ? 12 : 0));
      } else if (type === "minute") {
        newDate.setMinutes(parseInt(value));
      } else if (type === "ampm") {
        const currentHours = newDate.getHours();
        newDate.setHours(value === "PM" ? currentHours + 12 : currentHours - 12);
      }
      setDate?.(newDate);
    }
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant='outline'
          className={cn(
            "w-full justify-start text-left font-normal",
            !date && "text-muted-foreground"
          )}
        >
          <CalendarIcon className='mr-2 h-4 w-4' />
          {date ? moment(date).format("MM/DD/YYYY hh:mm A") : <span>Pick a date</span>}
        </Button>
      </PopoverTrigger>
      <PopoverContent className='w-auto p-0'>
        <div className='sm:flex'>
          <Calendar mode='single' selected={date} onSelect={handleDateSelect} initialFocus />
          <div className='flex flex-col sm:flex-row sm:h-[300px] divide-y sm:divide-y-0 sm:divide-x'>
            <ScrollArea className='w-64 sm:w-auto'>
              <div className='flex sm:flex-col p-2'>
                {hours.reverse().map((hour) => (
                  <Button
                    key={hour}
                    size='icon'
                    variant={date && date.getHours() % 12 === hour % 12 ? "default" : "ghost"}
                    className='sm:w-full shrink-0 aspect-square'
                    onClick={() => handleTimeChange("hour", hour.toString())}
                  >
                    {hour}
                  </Button>
                ))}
              </div>
              <ScrollBar orientation='horizontal' className='sm:hidden' />
            </ScrollArea>
            <ScrollArea className='w-64 sm:w-auto'>
              <div className='flex sm:flex-col p-2'>
                {Array.from({ length: 12 }, (_, i) => i * 5).map((minute) => (
                  <Button
                    key={minute}
                    size='icon'
                    variant={date && date.getMinutes() === minute ? "default" : "ghost"}
                    className='sm:w-full shrink-0 aspect-square'
                    onClick={() => handleTimeChange("minute", minute.toString())}
                  >
                    {minute}
                  </Button>
                ))}
              </div>
              <ScrollBar orientation='horizontal' className='sm:hidden' />
            </ScrollArea>
            <ScrollArea className=''>
              <div className='flex sm:flex-col p-2'>
                {["AM", "PM"].map((ampm) => (
                  <Button
                    key={ampm}
                    size='icon'
                    variant={
                      date &&
                      ((ampm === "AM" && date.getHours() < 12) ||
                        (ampm === "PM" && date.getHours() >= 12))
                        ? "default"
                        : "ghost"
                    }
                    className='sm:w-full shrink-0 aspect-square'
                    onClick={() => handleTimeChange("ampm", ampm)}
                  >
                    {ampm}
                  </Button>
                ))}
              </div>
            </ScrollArea>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
