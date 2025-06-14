import { Lecture } from "@/types/course.type";
import { Loader2 } from "lucide-react";
import { createContext, use, useState } from "react";

interface CourseDialogContextType {
  chapterId: string;
  lecture: Lecture;
  dialogOpen: string | null;
  setChapterId: React.Dispatch<React.SetStateAction<string | null>>;
  setLecture: React.Dispatch<React.SetStateAction<Lecture | null>>;
  setDialogOpen: React.Dispatch<React.SetStateAction<string | null>>;
  //   setVideoDialog: (option: "open" | "close") => void;
  //   setDescriptionDialog: (option: "open" | "close") => void;
  //   setAttachmentDialog: (option: "open" | "close") => void;
}

const CourseDialogContext = createContext<CourseDialogContextType | undefined>(undefined);

export function CourseDialogProvider({ children }: { children: React.ReactNode }) {
  const [dialogOpen, setDialogOpen] = useState<string | null>(null);
  const [chapterId, setChapterId] = useState<string | null>(null);
  const [lecture, setLecture] = useState<Lecture | null>(null);

  //   const handleSetChapterId = (chapterId: string) => {
  //     setChapterId(chapterId);
  //   };

  //   const handleSetLecture = (lecture: Lecture) => {
  //     setLecture(lecture);
  //   };

  //   const setVideoDialog = (option: "open" | "close") => {
  //     if (option === "open") {
  //       setDialogOpen(`${lecture?.id}-video`);
  //     } else {
  //       setDialogOpen(null);
  //     }
  //   };

  //   const setDescriptionDialog = (option: "open" | "close") => {
  //     if (option === "open") {
  //       setDialogOpen(`${lecture?.id}-description`);
  //     } else {
  //       setDialogOpen(null);
  //     }
  //   };

  //   const setAttachmentDialog = (option: "open" | "close") => {
  //     if (option === "open") {
  //       setDialogOpen(`${lecture?.id}-attachment`);
  //     } else {
  //       setDialogOpen(null);
  //     }
  //   };

  if (!lecture || !chapterId) {
    return <Loader2 className='size-4 animate-spin' />;
  }

  return (
    <CourseDialogContext.Provider
      value={{
        dialogOpen,
        chapterId,
        lecture,
        setChapterId,
        setLecture,
        setDialogOpen,
      }}
    >
      {children}
    </CourseDialogContext.Provider>
  );
}

export function useCourseDialog() {
  const context = use(CourseDialogContext);
  if (context === undefined) {
    throw new Error("useCourseDialog must be used within a CourseDialogProvider");
  }
  return context;
}
