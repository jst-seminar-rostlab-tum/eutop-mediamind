import React from "react";
import { ArticleBreadcrumb } from "~/custom-components/article/article-breadcrumb";
import { ArticleSidebar } from "~/custom-components/article/article-sidebar";
import type { Article } from "../../../types/model";
import { ArticleBody } from "~/custom-components/article/article-body";
import Layout from "~/custom-components/layout";

interface ArticleProps {
  searchProfileId: string;
  matchId: string;
  article: Article;
}

export function ArticlePage({ searchProfileId, article }: ArticleProps) {
  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);

      if (isNaN(date.getTime())) {
        return "Invalid Date";
      }

      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    } catch (error) {
      return "Invalid Date";
    }
  };

  const publishDateString = formatDate(article.published_at);

  return (
    <Layout>
      <div className="flex gap-15">
        <div className="w-3/4 space-y-6">
          <ArticleBreadcrumb searchProfileId={searchProfileId} />
          <ArticleBody
            title={article.title}
            content={article.content}
            published_at={publishDateString}
          />
        </div>
        <div className="w-1/4">
          <ArticleSidebar article={article} />
        </div>
      </div>
    </Layout>
  );
}
