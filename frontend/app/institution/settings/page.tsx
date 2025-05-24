"use client";
import React from "react";
// import { DragDropProvider } from "@dnd-kit/react";
import { useSortable } from "@dnd-kit/react/sortable";
// import { move } from "@dnd-kit/helpers";

export default function ExamplePage() {
  const items = [0, 1, 2, 3];

  return (
    <div className='flex flex-row gap-20'>
      {items.map((id, index) => (
        <Sortable key={id} id={id} index={index} />
      ))}
    </div>
  );
}

function Sortable({ id, index }: { id: number; index: number }) {
  const { ref } = useSortable({ id, index });

  return <button ref={ref}>Item {id}</button>;
}
