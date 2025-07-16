import React from "react";
import { ArticleBreadcrumb } from "~/custom-components/article/article-breadcrumb";
import { ArticleSidebar } from "~/custom-components/article/article-sidebar";
import type { ArticleMatch } from "../../../types/model";
import { ArticleBody } from "~/custom-components/article/article-body";
import Layout from "~/custom-components/layout";
import { formatDate, getLocalizedContent } from "~/lib/utils";
import { useTranslation } from "react-i18next";

interface ArticleProps {
  searchProfileId: string;
  matchId: string;
  article: ArticleMatch;
  searchProfileName: string;
}

export function ArticlePage({
  searchProfileId,
  article,
  searchProfileName,
}: ArticleProps) {
  const { i18n } = useTranslation();

  const publishDateString = formatDate(article.article.published);

  const localizedHeadline = getLocalizedContent(article.article.headline, i18n);
  const localizedText = getLocalizedContent(article.article.text, i18n);

  return (
    <Layout>
      <div className="flex gap-15">
        <div className="w-2/3 space-y-8">
          <ArticleBreadcrumb
            searchProfileId={searchProfileId}
            searchProfileName={searchProfileName}
            articleName={localizedHeadline}
          />
          <ArticleBody
            title={localizedHeadline}
            content={localizedText}
            published_at={publishDateString}
            {...(article.article.authors?.length
              ? { author: article.article.authors.join(", ") }
              : {})}
          />
        </div>
        <div className="w-1/3">
          <ArticleSidebar article={article} />
        </div>
      </div>
    </Layout>
  );
}
