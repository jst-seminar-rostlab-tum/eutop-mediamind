import { CrawlerStatsPage } from "~/pages/crawler-stats/crawler-stats";

export function meta() {
  return [
    { title: "MediaMind | Crawler Stats" },
    { name: "description", content: "Crawler Stats" },
  ];
}

export default function CrawlerStats() {
  return <CrawlerStatsPage />;
}
