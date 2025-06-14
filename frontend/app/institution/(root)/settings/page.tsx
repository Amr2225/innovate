"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Switch } from "@/components/ui/switch";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { CalendarIcon } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

interface PolicyData {
  min_passing_percentage: number;
  max_allowed_failures: number;
  min_gpa_required: number;
  min_attendance_percent: number;
  max_allowed_courses_per_semester: number;
  year_registration_open: boolean;
  summer_registration_open: boolean;
  promotion_time: Date;
}

export default function InstitutionPolicyPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [policyData, setPolicyData] = useState<PolicyData>({
    min_passing_percentage: 60,
    max_allowed_failures: 2,
    min_gpa_required: 2.0,
    min_attendance_percent: 75,
    max_allowed_courses_per_semester: 6,
    year_registration_open: true,
    summer_registration_open: false,
    promotion_time: new Date(),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      // TODO: Implement API call to update policy
      toast.success("Policy updated successfully");
    } catch {
      toast.error("Failed to update policy");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className='container max-w-4xl py-10'>
      <div className='space-y-6'>
        {/* Institution Access Code Section */}
        <Card>
          <CardHeader>
            <CardTitle>Institution Access Code</CardTitle>
          </CardHeader>
          <CardContent>
            <div className='flex items-center justify-between p-4 bg-muted rounded-lg'>
              <div className='space-y-1'>
                <p className='text-sm text-muted-foreground'>Your institution access code</p>
                <p className='text-2xl font-mono font-bold'>INST-2024-1234</p>
              </div>
              <Button
                variant='outline'
                onClick={() => {
                  navigator.clipboard.writeText("INST-2024-1234");
                  toast.success("Access code copied to clipboard");
                }}
              >
                Copy Code
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Policy Settings Form */}
        <form onSubmit={handleSubmit}>
          <Card>
            <CardHeader>
              <CardTitle>Academic Policy Settings</CardTitle>
            </CardHeader>
            <CardContent className='space-y-6'>
              <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
                {/* Minimum Passing Percentage */}
                <div className='space-y-2'>
                  <Label htmlFor='min_passing_percentage'>Minimum Passing Percentage</Label>
                  <Input
                    id='min_passing_percentage'
                    type='number'
                    min='0'
                    max='100'
                    value={policyData.min_passing_percentage}
                    onChange={(e) =>
                      setPolicyData({
                        ...policyData,
                        min_passing_percentage: Number(e.target.value),
                      })
                    }
                  />
                </div>

                {/* Maximum Allowed Failures */}
                <div className='space-y-2'>
                  <Label htmlFor='max_allowed_failures'>Maximum Allowed Failures</Label>
                  <Input
                    id='max_allowed_failures'
                    type='number'
                    min='0'
                    value={policyData.max_allowed_failures}
                    onChange={(e) =>
                      setPolicyData({
                        ...policyData,
                        max_allowed_failures: Number(e.target.value),
                      })
                    }
                  />
                </div>

                {/* Minimum GPA Required */}
                <div className='space-y-2'>
                  <Label htmlFor='min_gpa_required'>Minimum GPA Required</Label>
                  <Input
                    id='min_gpa_required'
                    type='number'
                    step='0.1'
                    min='0'
                    max='4'
                    value={policyData.min_gpa_required}
                    onChange={(e) =>
                      setPolicyData({
                        ...policyData,
                        min_gpa_required: Number(e.target.value),
                      })
                    }
                  />
                </div>

                {/* Minimum Attendance Percent */}
                <div className='space-y-2'>
                  <Label htmlFor='min_attendance_percent'>Minimum Attendance Percent</Label>
                  <Input
                    id='min_attendance_percent'
                    type='number'
                    min='0'
                    max='100'
                    value={policyData.min_attendance_percent}
                    onChange={(e) =>
                      setPolicyData({
                        ...policyData,
                        min_attendance_percent: Number(e.target.value),
                      })
                    }
                  />
                </div>

                {/* Maximum Allowed Courses */}
                <div className='space-y-2'>
                  <Label htmlFor='max_allowed_courses'>Maximum Courses per Semester</Label>
                  <Input
                    id='max_allowed_courses'
                    type='number'
                    min='1'
                    value={policyData.max_allowed_courses_per_semester}
                    onChange={(e) =>
                      setPolicyData({
                        ...policyData,
                        max_allowed_courses_per_semester: Number(e.target.value),
                      })
                    }
                  />
                </div>

                {/* Promotion Time */}
                <div className='space-y-2'>
                  <Label>Promotion Time</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant='outline'
                        className={cn(
                          "w-full justify-start text-left font-normal",
                          !policyData.promotion_time && "text-muted-foreground"
                        )}
                      >
                        <CalendarIcon className='mr-2 h-4 w-4' />
                        {policyData.promotion_time ? (
                          format(policyData.promotion_time, "PPP")
                        ) : (
                          <span>Pick a date</span>
                        )}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className='w-auto p-0'>
                      <Calendar
                        mode='single'
                        selected={policyData.promotion_time}
                        onSelect={(date) =>
                          date &&
                          setPolicyData({
                            ...policyData,
                            promotion_time: date,
                          })
                        }
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
              </div>

              {/* Registration Toggles */}
              <div className='space-y-4 pt-4'>
                <div className='flex items-center justify-between'>
                  <div className='space-y-0.5'>
                    <Label>Year Registration</Label>
                    <p className='text-sm text-muted-foreground'>
                      Allow students to register for the academic year
                    </p>
                  </div>
                  <Switch
                    checked={policyData.year_registration_open}
                    onCheckedChange={(checked) =>
                      setPolicyData({
                        ...policyData,
                        year_registration_open: checked,
                      })
                    }
                  />
                </div>

                <div className='flex items-center justify-between'>
                  <div className='space-y-0.5'>
                    <Label>Summer Registration</Label>
                    <p className='text-sm text-muted-foreground'>
                      Allow students to register for summer courses
                    </p>
                  </div>
                  <Switch
                    checked={policyData.summer_registration_open}
                    onCheckedChange={(checked) =>
                      setPolicyData({
                        ...policyData,
                        summer_registration_open: checked,
                      })
                    }
                  />
                </div>
              </div>

              <Button type='submit' className='w-full' disabled={isLoading}>
                {isLoading ? "Saving..." : "Save Changes"}
              </Button>
            </CardContent>
          </Card>
        </form>
      </div>
    </div>
  );
}
