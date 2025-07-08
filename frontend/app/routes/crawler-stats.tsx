import { useAuthorization } from "~/hooks/use-authorization";
import { CrawlerStatsPage } from "~/pages/crawler-stats/crawler-stats";
import { ErrorPage } from "~/pages/error/error";

export function meta() {
  return [
    { title: "MediaMind | Crawler Stats" },
    { name: "description", content: "Crawler Stats" },
  ];
}

export default function CrawlerStats() {
  const { user } = useAuthorization();

  if (!user?.is_superuser) {
    return <ErrorPage code={403} />;
  }

  return <CrawlerStatsPage />;
}
