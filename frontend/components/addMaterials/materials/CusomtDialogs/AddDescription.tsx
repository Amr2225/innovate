import React, { useRef } from "react";
import { useParams } from "next/navigation";

// Components
import CustomDialog from "@/components/CustomDialog";
import { registerLicense } from "@syncfusion/ej2-base";
import {
  HtmlEditor,
  Image,
  Inject,
  Link,
  QuickToolbar,
  RichTextEditorComponent,
  Toolbar,
  Table,
} from "@syncfusion/ej2-react-richtexteditor";

// Types
import { DialogGroupProps } from "../dialogGroup";

// Store
import { createCourseStore } from "@/store/courseStore";

// Styles
import styles from "./richTextEditor.module.css";

registerLicense(
  "Ngo9BigBOggjHTQxAR8/V1NNaF1cWmhIfEx1RHxQdld5ZFRHallYTnNWUj0eQnxTdEBjXH1WcnVXQGJUVkZ0X0lfag=="
);

export default function AddDescription({
  dialogOpen,
  setDialogOpen,
  lecture,
  chapterId,
}: DialogGroupProps) {
  const { courseId } = useParams();
  const useCourseStore = createCourseStore((courseId as string) || "new");
  const { updateLecture } = useCourseStore();
  const editorRef = useRef<RichTextEditorComponent>(null);

  const updateDescription = () => {
    if (editorRef.current) {
      updateLecture(chapterId, lecture.id, "description", editorRef.current.value);
    }
  };

  const toolbarSettings = {
    items: [
      "Bold",
      "Italic",
      "Underline",
      "StrikeThrough",
      "FontName",
      "FontSize",
      "FontColor",
      "BackgroundColor",
      "LowerCase",
      "UpperCase",
      "|",
      "Formats",
      "Alignments",
      "OrderedList",
      "UnorderedList",
      "Outdent",
      "Indent",
      "|",
      "CreateLink",
      "Image",
      "CreateTable",
      "|",
      "ClearFormat",
      "|",
      "Undo",
      "Redo",
    ],
  };

  return (
    <CustomDialog
      title='Description'
      description='Add a description for the lecture'
      open={dialogOpen === "description"}
      setOpen={(open) => setDialogOpen(open ? "description" : null)}
      contentClassName='!max-h-[80%] max-w-[75%]'
      closeOnClickOutside={false}
    >
      <div className={`${styles.editorContainer} h-[calc(80vh-120px)] overflow-hidden`}>
        <RichTextEditorComponent
          ref={editorRef}
          value={lecture.description}
          className='h-full w-full'
          toolbarSettings={toolbarSettings}
          height='100%'
          change={updateDescription}
        >
          <Inject services={[Toolbar, Image, Link, QuickToolbar, HtmlEditor, Table]} />
        </RichTextEditorComponent>
      </div>
    </CustomDialog>
  );
}
