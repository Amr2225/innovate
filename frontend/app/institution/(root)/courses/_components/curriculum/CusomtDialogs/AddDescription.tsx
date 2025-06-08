import React from "react";

// Components
import CustomDialog from "../../../../../../../components/CustomDialog";
// import TextEditor from "@/components/text-editor";

import { registerLicense } from "@syncfusion/ej2-base";
import {
  HtmlEditor,
  Image,
  Inject,
  Link,
  QuickToolbar,
  RichTextEditorComponent,
  Toolbar,
} from "@syncfusion/ej2-react-richtexteditor";

// Types
import { DialogGroupProps } from "../dialogGroup";

registerLicense(
  "Ngo9BigBOggjHTQxAR8/V1NNaF1cWmhIfEx1RHxQdld5ZFRHallYTnNWUj0eQnxTdEBjXH1WcnVXQGJUVkZ0X0lfag=="
);

export default function AddDescription({ dialogOpen, setDialogOpen }: DialogGroupProps) {
  return (
    <CustomDialog
      title='Description'
      description='Add a description for the lecture'
      open={dialogOpen === "description"}
      setOpen={(open) => setDialogOpen(open ? "description" : null)}
      contentClassName='!max-h-[80%]  max-w-[75%]'
    >
      {/* <TextEditor /> */}
      <RichTextEditorComponent onChange={(e) => console.log(e)} className='h-full'>
        <Inject services={[Toolbar, Image, Link, HtmlEditor, QuickToolbar]} />
      </RichTextEditorComponent>
    </CustomDialog>
  );
}
