import React from "react";
import { ArticleBreadcrumb } from "~/custom-components/article/article-breadcrumb";
import type { ArticleMatch } from "../../../types/model";
import { ArticleBody } from "~/custom-components/article/article-body";
import { formatDate, getLocalizedContent } from "~/lib/utils";
import i18n from "~/i18n";
import { MockedArticleSidebar } from "./mocked-article-sidebar";

interface ArticleProps {
  searchProfileId: string;
  matchId: string;
  article: ArticleMatch;
  searchProfileName: string;
}

export function MockedArticlePage({
  searchProfileId,
  article,
  searchProfileName,
}: ArticleProps) {
  const publishDateString = formatDate(article.article.published);
  const localizedHeadline = getLocalizedContent(article.article.headline, i18n);
  const localizedText = getLocalizedContent(article.article.text, i18n);

  const onlySummary = !(
    article.article.text?.["en"] && article.article.text?.["de"]
  );

  return (
    <div className="flex gap-15 overflow-auto p-6">
      <div className="w-2/3 space-y-8">
        <ArticleBreadcrumb
          searchProfileId={searchProfileId}
          searchProfileName={searchProfileName}
          articleName={localizedHeadline}
        />
        <ArticleBody
          title={localizedHeadline}
          content={
            onlySummary
              ? getLocalizedContent(article.article.summary, i18n)
              : localizedText
          }
          onlySummary={onlySummary}
          published_at={publishDateString}
          image_urls={["https://picsum.photos/800/600?random=1"]}
          {...(article.article.authors?.length
            ? { author: article.article.authors.join(", ") }
            : {})}
        />
      </div>
      <div className="w-1/3">
        <MockedArticleSidebar article={article} />
      </div>
    </div>
  );
}
