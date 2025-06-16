import type { Article } from "../../../types/model";
import { Button } from "~/components/ui/button";
import { ExternalLink } from "lucide-react";
import { ArticleMetaDataTable } from "~/custom-components/article/article-meta-data-table";

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
      <div className={"space-y-2"}>
        <h3 className={"font-bold"}>Summary:</h3>
        <p>{article.summary}</p>
      </div>
      <ArticleMetaDataTable article={article} />
    </div>
  );
}
