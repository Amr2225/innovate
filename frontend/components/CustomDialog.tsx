import React, { useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

type CustomDialogProps = {
  trigger?: React.ReactNode;
  title: string | React.ReactNode;
  description: string;
  children: React.ReactNode;
  open: boolean;
  contentClassName?: string;
  closeOnClickOutside?: boolean;
  setOpen: (open: boolean) => void;
};

export default function CustomDialog({
  trigger,
  title,
  description,
  children,
  open,
  setOpen,
  contentClassName,
  closeOnClickOutside = true,
}: CustomDialogProps) {
  useEffect(() => {
    if (!open) {
      setTimeout(() => {
        document.body.style.pointerEvents = "";
      }, 300);
    }
  }, [open]);

  const handleOpenChange = (newOpenState: boolean) => {
    if (newOpenState || closeOnClickOutside) {
      setOpen(newOpenState);
      if (!newOpenState) {
        setTimeout(() => {
          document.body.style.pointerEvents = "";
        }, 300);
      }
    }
  };

  const handleDialogButtonClose = (e: React.MouseEvent) => {
    const target = e.target as HTMLElement;

    const closeButton = target.closest("button.absolute.right-4.top-4");
    const svgIcon = target.closest("svg.h-4.w-4");

    if (closeButton || svgIcon) {
      e.stopPropagation();
      setOpen(false);
      setTimeout(() => {
        document.body.style.pointerEvents = "";
      }, 300);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className={contentClassName} onClick={handleDialogButtonClose}>
        <DialogHeader>
          {typeof title === "object" && React.isValidElement(title) ? (
            <>{title}</>
          ) : (
            <DialogTitle>{title}</DialogTitle>
          )}
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        <div>{children}</div>
      </DialogContent>
    </Dialog>
  );
}

{
  /* <div className='flex items-center gap-2'>
              <DialogTitle>{title}</DialogTitle>
              <HoverCard>
                <HoverCardTrigger asChild>
                  <Info className='size-4 text-primary cursor-help' />
                </HoverCardTrigger>
                <HoverCardContent>
                  <div className='space-y-2'>
                    <h4 className='text-sm font-semibold'>Edit Questions</h4>
                    <p className='text-sm text-muted-foreground'>
                      Double click on any question or option to edit it.
                    </p>
                  </div>
                </HoverCardContent>
              </HoverCard>
            </div> */
}
