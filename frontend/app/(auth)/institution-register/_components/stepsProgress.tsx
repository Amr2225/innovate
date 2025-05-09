import React from "react";

export default function StepsProgress({
  className,
  currentStep,
  steps,
}: {
  className?: string;
  currentStep: number;
  steps: number;
}) {
  return (
    <div className={`flex items-center justify-center ${className}`}>
      {Array(steps)
        .fill(0)
        .map((_, index) => (
          <React.Fragment key={index}>
            {/* Number of Steps */}
            <span
              className={`flex items-center justify-center rounded-full min-h-[50px] min-w-[50px] aspect-square border-2 ${
                index + 1 <= currentStep ? "border-primary" : "border-neutral-200 ease-in-out"
              } text-lg font-bold`}
            >
              {index + 1}
            </span>

            {/* Line between each number  */}
            {index < steps - 1 && (
              <span
                className={`after:transition-all w-full h-1 transition-all relative ease-[cubic-bezier(0.075, 0.82, 0.165, 1)] slide bg-neutral-200 ${
                  index + 2 <= currentStep ? "after:w-full" : "after:w-0"
                } `}
              />
            )}
          </React.Fragment>
        ))}
    </div>
  );
}
