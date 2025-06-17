import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";

import type { BreakingNews } from "../../../types/model";
import { ChevronDown, ChevronUp } from "lucide-react";
import { formatDate } from "~/lib/utils";

interface NewsCardProps {
  news: BreakingNews;
}

export function BreakingNewsCard({ news }: NewsCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const maxLength = 142;

  const shouldTruncate = news.description.length > maxLength;
  const displayText = isExpanded
    ? news.description
    : news.description.slice(0, maxLength) + (shouldTruncate ? "..." : "");

  return (
    <div className="border p-3 w-full  rounded-3xl flex gap-4">
      <div className={"overflow-hidden rounded-2xl w-27 h-27 flex-shrink-0"}>
        <img src={news.image} className="w-full h-full object-cover" />
      </div>
      <div>
        <div>
          <h2 className={"text-xl font-bold"}>{news.title}</h2>
        </div>
        <div className="flex-grow text-gray-600">
          <p className={"text-sm text-gray-400 mb-1"}>
            {formatDate(news.date)}
          </p>
          <p className="mb-2">{displayText}</p>
          {shouldTruncate && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-blue-600 hover:text-blue-800 font-medium transition-colors flex gap-2 items-center hover:cursor-pointer"
            >
              {isExpanded ? "Show less" : "Read more"}
              {isExpanded ? (
                <ChevronUp className={"w-4 h-4"} />
              ) : (
                <ChevronDown className={"w-4 h-4"} />
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
