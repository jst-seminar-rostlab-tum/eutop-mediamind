import { useState } from "react";

import { ChevronDown, ChevronUp, ExternalLink } from "lucide-react";
import { formatDate } from "~/lib/utils";
import { Button } from "~/components/ui/button";
import type { BreakingNewsItem } from "../../../types/model";
import { useTranslation } from "react-i18next";

interface NewsCardProps {
  news: BreakingNewsItem;
}

export function BreakingNewsCard({ news }: NewsCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const maxLength = 142;

  const { t } = useTranslation();
  const shouldTruncate = news.summary!.length > maxLength;
  const displayText = isExpanded
    ? news.summary
    : news.summary!.slice(0, maxLength) + (shouldTruncate ? "..." : "");

  return (
    <div className="border p-3 w-full  rounded-3xl flex gap-4">
      {news.image_url && (
        <div className={"overflow-hidden rounded-2xl w-27 h-28 flex-shrink-0"}>
          <img src={news.image_url!} className="w-full h-full object-cover" />
        </div>
      )}
      <div>
        <div>
          <h2 className={"text-xl font-bold"}>{news.title}</h2>
        </div>
        <div className="flex-grow text-gray-600">
          <p className={"text-sm text-gray-400 mb-1"}>
            {formatDate(formatDate(news.published_at!))}
          </p>
          <p className="mb-2">{displayText}</p>
          <div className={"flex gap-4"}>
            {shouldTruncate && (
              <Button
                variant="secondary"
                onClick={() => setIsExpanded(!isExpanded)}
                className=" font-medium p-1 h-auto"
              >
                {isExpanded
                  ? t("breaking-news.show_less")
                  : t("breaking-news.show_more")}
                {isExpanded ? (
                  <ChevronUp className="w-4 h-4 ml-2" />
                ) : (
                  <ChevronDown className="w-4 h-4 ml-2" />
                )}
              </Button>
            )}
            {news.url && (
              <Button asChild>
                <a href={news.url} target="_blank">
                  {t("breaking-news.original")}
                  <ExternalLink />
                </a>
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
