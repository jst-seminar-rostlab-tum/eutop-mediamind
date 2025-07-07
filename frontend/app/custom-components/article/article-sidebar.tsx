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
import { ExternalLink } from "lucide-react";
import { getPercentage } from "~/lib/utils";
import { getLocalizedContent } from "~/lib/utils";

interface ArticleSidebarProps {
  article: ArticleMatch;
}

export function ArticleSidebar({ article }: ArticleSidebarProps) {
  const { t } = useTranslation();
  return (
    <div className={"space-y-6"}>
      <Button asChild>
        <a href={article.article.article_url}>
          {t("article-page.original_header")}
          <ExternalLink />
        </a>
      </Button>
      <div className={"rounded-3xl pl-4 pr-4 bg-gray-100"}>
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
      <div className={"rounded-3xl border p-4 space-y-2"}>
        <span className={"font-bold"}>{t("article-page.keywords_header")}</span>
        <p className={"text-sm text-gray-400"}>
          {t("article-page.keywords_text")}
        </p>
        {article.topics.map((topic) => (
          <div className={"space-y-1 bg-gray-100 p-2 rounded-2xl"}>
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
              {topic.keywords?.map((keyword) => (
                <Badge className={"p-1.5 rounded-lg"}>{keyword}</Badge>
              ))}
            </div>
          </div>
        ))}
      </div>
      <ArticleMetaDataTable article={article} />
    </div>
  );
}
