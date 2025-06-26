import React from "react";
import { ArticleBreadcrumb } from "~/custom-components/article/article-breadcrumb";
import { ArticleSidebar } from "~/custom-components/article/article-sidebar";
import type { ArticleMatch } from "../../../types/model";
import { ArticleBody } from "~/custom-components/article/article-body";
import Layout from "~/custom-components/layout";
import { formatDate } from "~/lib/utils";
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

  const getLocale = (language: string) => {
    switch (language) {
      case "de":
        return "de-DE";
      case "en":
        return "en-US";
      default:
        return "en-US";
    }
  };
  const publishDateString = formatDate(
    article.article.published,
    getLocale(i18n.language),
  );

  return (
    <Layout>
      <div className="flex gap-15">
        <div className="w-2/3 space-y-8">
          <ArticleBreadcrumb
            searchProfileId={searchProfileId}
            searchProfileName={searchProfileName}
            articleName={article.article.headline["en"]}
          />
          <ArticleBody
            title={
              article.article.headline["en"]
                ? article.article.headline["en"]
                : article.article.headline["de"]
            }
            content={
              article.article.text["en"]
                ? article.article.text["en"]
                : article.article.text["de"]
            }
            published_at={publishDateString}
            author={
              article.article.authors
                ? article.article.authors?.join(", ")
                : "Unknown"
            }
          />
        </div>
        <div className="w-1/3">
          <ArticleSidebar article={article} />
        </div>
      </div>
    </Layout>
  );
}
