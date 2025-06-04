import { Label } from "~/components/ui/label";
import { Plus } from "lucide-react";

interface AiSuggestionTagProps {
  keyword: string;
}

export function AiSuggestionTag({ keyword }: AiSuggestionTagProps) {
  return (
    <div
      className={"inline-flex p-1.5 rounded-md items-center gap-1 bg-gray-100 "}
    >
      <Label
        className={
          "bg-gradient-to-r from-blue-600 via-purple-500 to-pink-400 inline-block text-transparent bg-clip-text p-1"
        }
      >
        {keyword}
      </Label>
      <div
        className={
          "hover:bg-gray-200 transition-colors duration-200 rounded-xs p-0.5"
        }
      >
        <Plus strokeWidth={"3"} className={"h-3.5 w-3.5 text-gray-400"} />
      </div>
    </div>
  );
}
