import { formatDate, getLocalizedContent } from "~/lib/utils";
import { Button } from "~/components/ui/button";
import type { BreakingNewsItem } from "../../../types/model";
import { useTranslation } from "react-i18next";
import { ExternalLink } from "lucide-react";

interface NewsCardProps {
  news: BreakingNewsItem;
}

export function BreakingNewsCard({ news }: NewsCardProps) {

  const { t, i18n } = useTranslation();

  const headline = news.headline
    ? getLocalizedContent(news.headline, i18n)
    : "";
  const summary = news.summary ? getLocalizedContent(news.summary, i18n) : "";

  const displayText = summary + "...";

  return (
    <div className="border p-3 w-full rounded-lg flex gap-4">
      {news.image_url && (
        <div className="relative flex-shrink-0 w-[200px]">
          <div className="absolute inset-0">
            <img
              src={news.image_url!}
              className="w-full h-full object-cover rounded-lg"
            />
          </div>
        </div>
      )}
      <div className="flex flex-col justify-between flex-grow">
        <div>
          <h2 className="text-xl font-bold">{headline}</h2>
        </div>
        <div className="text-gray-600">
          <p className="text-sm text-gray-400 mb-1">
            {formatDate(formatDate(news.published_at!))}
          </p>
          <p className="mb-2">{displayText}</p>
          <div className="flex gap-4">
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
