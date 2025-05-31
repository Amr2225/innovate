"use client";
// TODO:Delete this file this is only for refrence if needed
import React, { useMemo, useRef, useState } from "react";
// import TextEditor from "react-froala-wysiwyg";
import dynamic from "next/dynamic";
import HTMLReactParser from "html-react-parser";
import { Loader2 } from "lucide-react";
// import DOMPurify from "dompurify";

// Dynamically import JoditEditor with ssr disabled
const JoditEditor = dynamic(() => import("jodit-react"), {
  ssr: false,
  loading: () => <Loader2 className='animate-spin size-12 w-[95%] mx-auto text-primary' />,
});

export default function CoursePreviewPage() {
  const editor = useRef(null);
  const [content, setContent] = useState("");

  // Secure the HTML both in the editor and when displaying it
  const config = useMemo(
    () => ({
      readonly: false,
      placeholder: "Lecture Description",
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
        "ul",
        "ol",
        "font",
        "fontsize",
        "paragraph",
        "link",
        "image",
        "video",
        "table",
      ],
      // Basic image security - disable direct URL input
      // image: {
      //   dialogWidth: 600,
      //   selectImageFromUploader: true,
      //   editSettings: {
      //     resize: true,
      //     crop: true,
      //     sources: false,
      //     openOnDblClick: true,
      //   },
      // },
      // Remove "powered by Jodit" message
      hidePoweredByJodit: true,
    }),
    []
  );

  // // Function to sanitize HTML before displaying it
  // const sanitizeContent = (html: string) => {
  //   if (typeof window === "undefined") return html; // Server-side safety

  //   // First pass of sanitization
  //   const clean = DOMPurify.sanitize(html, {
  //     ALLOWED_TAGS: [
  //       "p",
  //       "br",
  //       "strong",
  //       "em",
  //       "u",
  //       "h1",
  //       "h2",
  //       "h3",
  //       "h4",
  //       "h5",
  //       "h6",
  //       "ul",
  //       "ol",
  //       "li",
  //       "a",
  //       "table",
  //       "tbody",
  //       "tr",
  //       "td",
  //       "th",
  //       "img",
  //     ],
  //     FORBID_TAGS: ["script", "style", "iframe", "form", "object", "embed", "svg"],
  //   });

  //   // Use DOM manipulation to handle images and links more securely
  //   const tempDiv = document.createElement("div");
  //   tempDiv.innerHTML = clean;

  //   // Secure all links
  //   const links = tempDiv.querySelectorAll("a");
  //   links.forEach((link) => {
  //     if (link.hasAttribute("href")) {
  //       // Add security attributes to links
  //       link.setAttribute("rel", "noopener noreferrer");
  //       link.setAttribute("target", "_blank");
  //     }
  //   });

  //   // Secure all images
  //   const images = tempDiv.querySelectorAll("img");
  //   images.forEach((img) => {
  //     if (img.hasAttribute("src")) {
  //       const src = img.getAttribute("src");
  //       // Remove unsafe image sources
  //       if (
  //         src &&
  //         (src.startsWith("javascript:") ||
  //           src.startsWith("data:") ||
  //           !src.match(/^(https?:\/\/|\/)/i))
  //       ) {
  //         img.setAttribute("src", "");
  //       }
  //     }
  //   });

  //   // Second pass of sanitization to be sure
  //   return DOMPurify.sanitize(tempDiv.innerHTML);
  // };

  return (
    <div>
      <JoditEditor
        ref={editor}
        value={content}
        config={config}
        tabIndex={1}
        onBlur={(newContent) => setContent(newContent)}
      />
      <div>{HTMLReactParser(content)}</div>
    </div>
  );
}
