import React from "react";
import { ArticleBreadcrumb } from "~/custom-components/article/article-breadcrumb";
import { ArticleSidebar } from "~/custom-components/article/article-sidebar";
import type { Article } from "../../../types/model";
import { ArticleBody } from "~/custom-components/article/article-body";
import Layout from "~/custom-components/layout";
import { formatDate } from "~/lib/utils";

interface ArticleProps {
  searchProfileId: string;
  matchId: string;
  article: Article;
  searchProfileName: string;
}

export function ArticlePage({
  searchProfileId,
  article,
  searchProfileName,
}: ArticleProps) {
  const publishDateString = formatDate(article.published_at);

  return (
    <Layout>
      <div className="flex gap-15">
        <div className="w-2/3 space-y-8">
          <ArticleBreadcrumb
            searchProfileId={searchProfileId}
            searchProfileName={searchProfileName}
            articleName={article.title}
          />
          <ArticleBody
            title={article.title}
            content={article.content}
            published_at={publishDateString}
            author={article.author}
          />
        </div>
        <div className="w-1/3">
          <ArticleSidebar article={article} />
        </div>
      </div>
    </Layout>
  );
}
