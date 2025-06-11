import { Label } from "~/components/ui/label";
import { Plus } from "lucide-react";

interface AiSuggestionTagProps {
  keyword: string;
  onAdd: (keyword: string) => void;
}

export function AiSuggestionTag({ keyword, onAdd }: AiSuggestionTagProps) {
  const handlePlusClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onAdd(keyword);
  };

  return (
    <div
      className={"inline-flex p-1.5 rounded-md items-center gap-1 bg-gray-100"}
    >
      <Label
        className={
          "bg-gradient-to-r from-blue-800 via-purple-800 to-pink-800 inline-block text-transparent bg-clip-text p-1"
        }
      >
        {keyword}
      </Label>
      <div
        className={
          "hover:bg-gray-200 transition-colors duration-200 rounded-xs p-0.5 cursor-pointer"
        }
        onClick={handlePlusClick}
      >
        <Plus strokeWidth={"3"} className={"h-3.5 w-3.5 text-gray-400"} />
      </div>
    </div>
  );
}
