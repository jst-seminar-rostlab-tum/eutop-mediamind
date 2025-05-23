import { X } from "lucide-react";

interface KeywordTagProps {
  name: string
}

export function KeywordTag({name}: KeywordTagProps){
  return (
    <div className={"inline-flex p-1.5 rounded-md border border-gray-300 items-center gap-1"}>
      <div >
        <X className={"h-4 w-4"}/>
      </div>
      {name}
    </div>
  )
}