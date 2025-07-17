import type { ArticleMatch } from "../../../types/model";
import { ArticleMetaDataTable } from "~/custom-components/article/article-meta-data-table";
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
} from "~/components/ui/accordion";
import { AccordionContent } from "@radix-ui/react-accordion";
import { Badge } from "~/components/ui/badge";
import { useTranslation } from "react-i18next";
import { Button } from "~/components/ui/button";
import { ExternalLink, ChevronDown, ChevronUp } from "lucide-react";
import { getPercentage } from "~/lib/utils";
import { getLocalizedContent } from "~/lib/utils";
import { useState } from "react";
import { ArticleEntities } from "~/custom-components/article/article-entities";

interface ArticleSidebarProps {
  article: ArticleMatch;
}

export function ArticleSidebar({ article }: ArticleSidebarProps) {
  const { t } = useTranslation();
  const [expandedTopics, setExpandedTopics] = useState<Record<number, boolean>>(
    {},
  );

  const toggleTopic = (topicIndex: number) => {
    setExpandedTopics((prev) => ({
      ...prev,
      [topicIndex]: !prev[topicIndex],
    }));
  };

  return (
    <div className={"space-y-6"}>
      <Button asChild>
        <a href={article.article.article_url}>
          {t("article-page.original_header")}
          <ExternalLink />
        </a>
      </Button>
      <div className={"rounded-lg pl-4 pr-4 bg-gray-100"}>
        <Accordion
          type={"single"}
          collapsible
          className="w-full"
          defaultValue="summary"
        >
          <AccordionItem value={"summary"}>
            <AccordionTrigger
              className={"text-md font-semibold text-gray-900 cursor-pointer"}
            >
              {t("article-page.summary_header")}
            </AccordionTrigger>
            <AccordionContent
              className={"text-gray-800 pb-4 whitespace-pre-wrap"}
            >
              <p>
                {getLocalizedContent(article.article.summary) ||
                  t("article-page.no_summary")}
              </p>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
      <div className={"rounded-lg border p-4 space-y-2"}>
        <span className={"font-bold"}>{t("article-page.keywords_header")}</span>
        <p className={"text-sm text-gray-400"}>
          {t("article-page.keywords_text")}
        </p>
        {article.topics.map((topic, topicIndex) => {
          const keywords = topic.keywords || [];
          const isExpanded = expandedTopics[topicIndex];
          const displayedKeywords = isExpanded
            ? keywords
            : keywords.slice(0, 5);
          const hasMoreKeywords = keywords.length > 5;

          return (
            <div
              key={topicIndex}
              className={"space-y-1 bg-gray-100 p-2 rounded-lg"}
            >
              <div className={"flex items-center gap-2"}>
                <p className={"font-bold text-gray-800"}>{topic.name}</p>
                <Badge
                  className={"p-1.5 rounded-lg"}
                  style={{
                    backgroundColor: `rgb(${Math.round(200 * (1 - topic.score)) + 55}, ${Math.round(200 * topic.score) + 55}, 100)`,
                  }}
                >
                  {getPercentage(topic.score)}
                </Badge>
              </div>
              <div className={"flex flex-wrap gap-1 pt-1"}>
                {displayedKeywords.map((keyword, keywordIndex) => (
                  <Badge key={keywordIndex} className={"p-1.5 rounded-lg"}>
                    {keyword}
                  </Badge>
                ))}
              </div>
              {hasMoreKeywords && (
                <Button
                  variant="link"
                  size="sm"
                  onClick={() => toggleTopic(topicIndex)}
                  className={"h-auto p-1.5 rounded-lg text-sm text-gray-600"}
                >
                  {isExpanded ? (
                    <>
                      {t("article-page.show_less")}
                      <ChevronUp size={14} />
                    </>
                  ) : (
                    <>
                      {t("article-page.show_more")} ({keywords.length - 5})
                      <ChevronDown size={14} />
                    </>
                  )}
                </Button>
              )}
            </div>
          );
        })}
      </div>
      {article.entities && <ArticleEntities entities={article.entities} />}
      <ArticleMetaDataTable article={article} />
    </div>
  );
}
