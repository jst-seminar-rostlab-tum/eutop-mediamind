import { type BreakingNewsResponse } from "~/pages/breaking-news/breaking-news-mock-data";
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
    data: response,
    isLoading,
    error,
  } = useQuery("/api/v1/crawler/get_breaking_news");

  const breakingNews = response as BreakingNewsResponse;

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

  console.log(breakingNews.results);

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
        {breakingNews.results.map((news) => (
          <BreakingNewsCard news={news} />
        ))}
      </div>
    </Layout>
  );
}
