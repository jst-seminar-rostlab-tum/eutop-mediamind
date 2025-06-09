import { X } from "lucide-react";
import { Label } from "~/components/ui/label";

interface KeywordTagProps {
  name: string;
  onDelete: (name: string) => void;
}
export function KeywordTag({ name, onDelete }: KeywordTagProps) {
  return (
    <div
      className={"inline-flex p-1.5 rounded-md items-center gap-1 bg-gray-100"}
    >
      <Label>{name}</Label>
      <button
        onClick={() => onDelete(name)}
        className={
          "cursor-pointer hover:bg-gray-200 transition-colors duration-200 rounded-xs p-0.5"
        }
      >
        <X strokeWidth={"3"} className={"h-3.5 w-3.5 text-gray-400"} />
      </button>
    </div>
  );
}
