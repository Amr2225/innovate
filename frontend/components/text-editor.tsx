import React, { useRef, useState } from "react";
import dynamic from "next/dynamic";
import { Loader2 } from "lucide-react";
import type { IJodit } from "jodit/types";

// Dynamically import JoditEditor with ssr disabled
const JoditEditor = dynamic(() => import("jodit-react"), {
  ssr: false,
  loading: () => <Loader2 className='animate-spin size-12 w-[95%] mx-auto text-primary' />,
});

export default function TextEditor() {
  const editor = useRef(null);
  const [content, setContent] = useState("");

  const config = {
    readonly: false,
    height: 400,
    zIndex: 1000, // Increase z-index to ensure menus appear above other elements
    useSearch: false,
    spellcheck: false,
    toolbarAdaptive: false,
    showCharsCounter: false,
    showWordsCounter: false,
    showXPathInStatusbar: false,
    askBeforePasteHTML: false,
    askBeforePasteFromWord: false,
    minHeight: 200,
    maxHeight: 800,
    uploader: {
      insertImageAsBase64URI: true,
    },
    placeholder: "",
    // Disable dangerous buttons
    removeButtons: ["source", "fullsize", "about", "print", "hr", "eraser", "classSpan"],
    // Limit allowed tags to prevent XSS
    cleanHTML: {
      allowTags:
        "p,br,strong,em,u,h1,h2,h3,h4,h5,h6,ul,ol,li,a[href|target],img[src|alt|width|height],table,tbody,tr,td,th",
      safeJavaScriptLink: true,
      removeOnError: true,
      denyTags: "script,iframe,object,embed,form,input,style,svg",
    },
    // Define allowed buttons
    buttons: [
      "bold",
      "italic",
      "underline",
      "strikethrough",
      "|",
      "ul",
      "ol",
      "|",
      "outdent",
      "indent",
      "|",
      "font",
      "fontsize",
      "paragraph",
      "|",
      "link",
      "image",
      "video",
      "table",
      "|",
      "align",
      "undo",
      "redo",
      "|",
      "cut",
      "copy",
      "paste",
      "|",
      "hr",
      "table",
    ],
    hidePoweredByJodit: true,
    // iframe: true,
    // iframeStyle: "html{margin:0}body{padding:0px}",
    // buttons:
    //   "bold,italic,underline,strikethrough,eraser,|,ul,ol,|,outdent,indent,|,font,fontsize,paragraph,|,link,|,align,undo,redo,\n,cut,copy,paste,|,hr,table,|,symbols,selectall,source",
    // extraButtons: ["fullsize"],
    // Fix menu positioning
    defaultMenuContainer: editor,
    // Ensure popup positioning works correctly
    popup: {
      appendTo: editor,
    },
    events: {
      afterInit: (editor: IJodit) => {
        // Force recalculation of popup positions
        editor.e.on("showPopup", () => {
          setTimeout(() => {
            editor.e.fire("updatePosition");
          }, 1000);
        });
      },
    },
  };

  return (
    <JoditEditor
      ref={editor}
      value={content}
      config={config}
      //   tabIndex={1}
      onBlur={(newContent) => setContent(newContent)}
      className='h-full'
      id='editor'
    />
  );
}
