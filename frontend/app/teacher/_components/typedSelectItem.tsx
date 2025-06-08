import { SelectItem } from "@/components/ui/select";

export default function TypedSelectItem<T extends string | null>({
  value,
  ...props
}: { value: T } & Omit<React.ComponentProps<typeof SelectItem>, "value">) {
  return <SelectItem value={value as string} {...props} />;
}
