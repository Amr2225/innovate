"use client";
// import React, { useEffect } from "react";
// import { DragDropProvider } from "@dnd-kit/react";
// import { useSortable } from "@dnd-kit/react/sortable";
// // import { move } from "@dnd-kit/helpers";

// const items = [0, 1, 2, 3];
// export default function ExamplePage() {
//   useEffect(() => {
//     console.log("items", items);
//   }, []);

//   const handleDragEnd = (event: unknown) => {
//     console.log("event", event);
//     // move(items, event.active.id, event.over?.id);
//     // move()
//   };

//   return (
//     <DragDropProvider onDragEnd={handleDragEnd}>
//       <div className='flex flex-row gap-20'>
//         {items.map((id, index) => (
//           <Sortable key={id} id={id} index={index} />
//         ))}
//       </div>
//     </DragDropProvider>
//   );
// }

import React, { useState } from "react";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";

import { CSS } from "@dnd-kit/utilities";

export default function ExamplePage() {
  const [items, setItems] = useState([1, 2, 3]);
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={items} strategy={verticalListSortingStrategy}>
        {items.map((id) => (
          <SortableItem key={id} id={id} />
        ))}
      </SortableContext>
    </DndContext>
  );

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;

    if (!over) return;

    if (active.id !== over.id) {
      setItems((items) => {
        const oldIndex = items.indexOf(active.id as number);
        const newIndex = items.indexOf(over.id as number);

        return arrayMove(items, oldIndex, newIndex);
      });
    }
  }
}

export function SortableItem(props: { id: number }) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({
    id: props.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <button>Item {props.id}</button>
    </div>
  );
}

// function Sortable({ id }: { id: number }) {
//   const { setNodeRef } = useSortable({ id });

//   return (
//     <div className='flex flex-row gap-20'>
//       <button ref={setNodeRef}>Item {id}</button>
//     </div>
//   );
// }
