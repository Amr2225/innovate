import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function SettingsSkeleton() {
  return (
    <div className='container max-w-4xl py-10'>
      <div className='space-y-6'>
        {/* Institution Access Code Skeleton */}
        <Card>
          <CardHeader>
            <CardTitle>Institution Access Code</CardTitle>
          </CardHeader>
          <CardContent>
            <div className='flex items-center justify-between p-4 bg-muted rounded-lg'>
              <div className='space-y-2'>
                <Skeleton className='h-4 w-32' />
                <Skeleton className='h-8 w-48' />
              </div>
              <Skeleton className='h-10 w-24' />
            </div>
          </CardContent>
        </Card>

        {/* Policy Settings Skeleton */}
        <Card>
          <CardHeader>
            <CardTitle>Academic Policy Settings</CardTitle>
          </CardHeader>
          <CardContent className='space-y-6'>
            <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
              {/* Input Fields Skeleton */}
              {Array.from({ length: 6 }).map((_, index) => (
                <div key={index} className='space-y-2'>
                  <Skeleton className='h-4 w-32' />
                  <Skeleton className='h-10 w-full' />
                </div>
              ))}
            </div>

            {/* Toggle Switches Skeleton */}
            <div className='space-y-4 pt-4'>
              {Array.from({ length: 2 }).map((_, index) => (
                <div
                  key={index}
                  className='flex items-center justify-between rounded-lg border p-4'
                >
                  <div className='space-y-2'>
                    <Skeleton className='h-4 w-32' />
                    <Skeleton className='h-4 w-48' />
                  </div>
                  <Skeleton className='h-6 w-11' />
                </div>
              ))}
            </div>

            {/* Submit Button Skeleton */}
            <Skeleton className='h-10 w-full' />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
