import React from "react";

// Types
import { Lecture } from "@/types/course.type";

// Dialogs
import AddVideoDialog from "./CusomtDialogs/AddVideoDialog";
import AddDescription from "./CusomtDialogs/AddDescription";
import AddAttachmentDialog from "./CusomtDialogs/AddAttachemetns";

export interface DialogGroupProps {
  dialogOpen: string | null;
  setDialogOpen: React.Dispatch<React.SetStateAction<string | null>>;
  lecture: Lecture;
  chapterId: string;
}

export default function DialogGroup({
  dialogOpen,
  setDialogOpen,
  lecture,
  chapterId,
}: DialogGroupProps) {
  return (
    <>
      <AddVideoDialog
        dialogOpen={dialogOpen}
        setDialogOpen={setDialogOpen}
        lecture={lecture}
        chapterId={chapterId}
      />

      <AddDescription
        dialogOpen={dialogOpen}
        setDialogOpen={setDialogOpen}
        lecture={lecture}
        chapterId={chapterId}
      />

      <AddAttachmentDialog
        dialogOpen={dialogOpen}
        setDialogOpen={setDialogOpen}
        lecture={lecture}
        chapterId={chapterId}
      />
    </>
  );
}
