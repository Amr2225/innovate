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
  title: string;
  description: string;
  children: React.ReactNode;
  open: boolean;
  setOpen: (open: boolean) => void;
  contentClassName?: string;
};

export default function CustomDialog({
  trigger,
  title,
  description,
  children,
  open,
  setOpen,
  contentClassName,
}: CustomDialogProps) {
  return (
    <Dialog
      open={open}
      onOpenChange={(open) => {
        setOpen(open);
        if (!open) {
          setTimeout(() => {
            document.body.style.pointerEvents = "";
          }, 300);
        }
      }}
    >
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className={contentClassName}>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        {children}
      </DialogContent>
    </Dialog>
  );
}
