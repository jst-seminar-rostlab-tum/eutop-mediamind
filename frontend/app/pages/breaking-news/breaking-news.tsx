import { getBreakingNews } from "~/pages/breaking-news/breaking-news-mock-data";
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

export function BreakingNews() {
  const breakingNews = getBreakingNews();
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
        {breakingNews.map((news) => (
          <BreakingNewsCard news={news} />
        ))}
      </div>
    </Layout>
  );
}
