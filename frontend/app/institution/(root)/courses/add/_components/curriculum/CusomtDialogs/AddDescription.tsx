import React, { useEffect, useState } from "react";

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
  ChangeEventArgs,
  Count,
  Lists,
} from "@syncfusion/ej2-react-richtexteditor";

// Types
import { DialogGroupProps } from "../dialogGroup";

registerLicense(
  "Ngo9BigBOggjHTQxAR8/V1NNaF1cWmhIfEx1RHxQdld5ZFRHallYTnNWUj0eQnxTdEBjXH1WcnVXQGJUVkZ0X0lfag=="
);

export default function AddDescription({ dialogOpen, setDialogOpen }: DialogGroupProps) {
  const [description, setDescription] = useState<string>("");

  // Handle change in the rich text editor
  const handleEditorChange = (e: ChangeEventArgs) => {
    const htmlContent = e.value || "";
    setDescription(htmlContent);
  };

  useEffect(() => {
    console.log(description);
  }, [description]);

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
      "|",
      "ClearFormat",
      "Print",
      "SourceCode",
      "FullScreen",
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
      contentClassName='!max-h-[80%]  max-w-[75%]'
    >
      {/* <TextEditor /> */}
      <div>
        {/* <RichTextEditorComponent
          onChange={handleEditorChange}
          value={description}
          className='h-full'
          toolbarSettings={toolbarSettings}
        >
          <Inject services={[Toolbar, HtmlEditor]} />
        </RichTextEditorComponent> */}
      </div>
    </CustomDialog>
  );
}

{
  /* <Inject services={[Toolbar, Image, Link, QuickToolbar, Count, Lists]} /> */
}
