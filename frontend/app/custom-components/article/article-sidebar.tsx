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
      <div className={"rounded-3xl border p-4"}>
        <span>Keywords</span>
        <div className={"flex flex-wrap gap-1 pt-1"}>
          {article.topic.keywords.map((keyword) => (
            <Badge className={"p-1.5 rounded-lg"}>{keyword}</Badge>
          ))}
        </div>
      </div>
      <ArticleMetaDataTable article={article} />
    </div>
  );
}
