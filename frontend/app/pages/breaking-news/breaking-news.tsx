import { BreakingNewsCard } from "~/custom-components/breaking-news/breaking-news-card";
import Layout from "~/custom-components/layout";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "~/components/ui/breadcrumb";
import { useQuery } from "../../../types/api";
import { ErrorPage } from "~/pages/error/error";
import { useTranslation } from "react-i18next";

export function BreakingNews() {
  const {
    data: breakingNews,
    isLoading,
    error,
  } = useQuery("/api/v1/crawler/get_breaking_news");

  const { t } = useTranslation();

  if (isLoading) {
    return (
      <Layout>
        <div>{t("breaking-news.news_loading")}</div>
      </Layout>
    );
  }

  if (error) {
    return <ErrorPage />;
  }

  return (
    <Layout>
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/dashboard">
              {t("breadcrumb_home")}
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>{t("breaking-news.header")}</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <h1 className="text-3xl font-bold mb-2">{t("breaking-news.header")}</h1>
      {!breakingNews || !breakingNews.news || breakingNews.news.length === 0 ? (
        <div className={"text-gray-400"}>{t("breaking-news.no_news")}</div>
      ) : (
        <>
          <div className="space-y-4">
            {breakingNews.news.map((news) => (
              <BreakingNewsCard key={news.id} news={news} />
            ))}
          </div>
        </>
      )}
    </Layout>
  );
}
