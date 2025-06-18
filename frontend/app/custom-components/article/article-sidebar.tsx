import type { Article } from "../../../types/model";
import { Button } from "~/components/ui/button";
import { ExternalLink } from "lucide-react";
import { ArticleMetaDataTable } from "~/custom-components/article/article-meta-data-table";
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
} from "~/components/ui/accordion";
import { AccordionContent } from "@radix-ui/react-accordion";
import { Badge } from "~/components/ui/badge";

interface ArticleSidebarProps {
  article: Article;
}

export function ArticleSidebar({ article }: ArticleSidebarProps) {
  return (
    <div className={"space-y-6"}>
      <Button asChild>
        <a href={article.url}>
          Original
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
            <AccordionTrigger className={"text-md font-semibold text-gray-900"}>
              Summary
            </AccordionTrigger>
            <AccordionContent className={"text-gray-800 pb-4"}>
              <p>{article.summary}</p>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
      <div className={"rounded-3xl border p-4 space-y-2"}>
        <span className={"font-bold"}>Keywords</span>
        <p className={"text-sm text-gray-400"}>
          Displays matched profile topics with keywords, and a score indicating
          topic relevance to the article.
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
                {topic.score}
              </Badge>
            </div>
            <div className={"flex flex-wrap gap-1 pt-1"}>
              {topic.keywords.map((keyword) => (
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
