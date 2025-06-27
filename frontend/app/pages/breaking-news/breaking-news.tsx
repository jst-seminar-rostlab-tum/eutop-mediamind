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

export function BreakingNews() {
  const {
    data: breakingNews,
    isLoading,
    error,
  } = useQuery("/api/v1/crawler/get_breaking_news");

  if (isLoading) {
    return (
      <Layout>
        <div>Loading breaking news...</div>
      </Layout>
    );
  }

  if (error) {
    return <ErrorPage />;
  }

  if (!breakingNews || !breakingNews.news) {
    return (
      <Layout>
        <div>No breaking news available</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/dashboard">Home</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Breaking News</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <h1 className="text-3xl font-bold mb-2">Breaking News</h1>
      <div className={"space-y-4 "}>
        {breakingNews.news.map((news) => (
          <BreakingNewsCard news={news} />
        ))}
      </div>
    </Layout>
  );
}
