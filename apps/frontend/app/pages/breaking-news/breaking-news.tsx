import { BreakingNewsCard } from "~/custom-components/breaking-news/breaking-news-card";
import { BreakingNewsCardSkeleton } from "~/custom-components/breaking-news/breaking-news-card-skeleton";
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
import { Link } from "react-router";
import Text from "~/custom-components/text";

export function BreakingNews() {
  const {
    data: breakingNews,
    isLoading,
    error,
  } = useQuery("/api/v1/crawler/get_breaking_news");

  const { t } = useTranslation();

  if (error) {
    return <ErrorPage />;
  }

  return (
    <Layout>
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link to="/dashboard">{t("breadcrumb_home")}</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>{t("breaking-news.header")}</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <Text hierachy={2}>{t("breaking-news.header")}</Text>

      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, index) => (
            <BreakingNewsCardSkeleton key={index} />
          ))}
        </div>
      ) : !breakingNews ||
        !breakingNews.news ||
        breakingNews.news.length === 0 ? (
        <div className={"text-gray-400"}>{t("breaking-news.no_news")}</div>
      ) : (
        <div className="space-y-4">
          {breakingNews.news.map((news) => (
            <BreakingNewsCard key={news.id} news={news} />
          ))}
        </div>
      )}
    </Layout>
  );
}
