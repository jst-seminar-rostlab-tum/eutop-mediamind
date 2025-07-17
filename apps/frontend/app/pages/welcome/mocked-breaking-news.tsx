import { BreakingNewsCard } from "~/custom-components/breaking-news/breaking-news-card";
import { useTranslation } from "react-i18next";
import Text from "~/custom-components/text";
import { sortBy } from "lodash-es";

export function MockedBreakingNews() {
  const { t } = useTranslation();

  const breakingNews = [
    {
      id: "1",
      title: t("mock_data.breaking_title_1"),
      summary: t("mock_data.breaking_summary_1"),
      image_url: "https://picsum.photos/800/600?random=1",
      url: "",
      published_at: "2025-07-16T09:00:00Z",
    },
    {
      id: "2",
      title: t("mock_data.breaking_title_2"),
      summary: t("mock_data.breaking_summary_2"),
      image_url: "https://picsum.photos/800/600?random=2",
      url: "",
      published_at: "2025-07-15T13:30:00Z",
    },
    {
      id: "3",
      title: t("mock_data.breaking_title_3"),
      summary: t("mock_data.breaking_summary_3"),
      image_url: "https://picsum.photos/800/600?random=3",
      url: "",
      published_at: "2025-07-14T08:45:00Z",
    },
    {
      id: "4",
      title: t("mock_data.breaking_title_4"),
      summary: t("mock_data.breaking_summary_4"),
      image_url: "https://picsum.photos/800/600?random=4",
      url: "",
      published_at: "2025-07-13T10:15:00Z",
    },
  ];

  const sortedNews = sortBy(breakingNews ?? [], "created_at").reverse();

  return (
    <div className="overflow-auto">
      <Text hierachy={2}>{t("breaking-news.header")}</Text>
      <div className="space-y-4">
        {sortedNews.map((news) => (
          <BreakingNewsCard key={news.id} news={news} />
        ))}
      </div>
    </div>
  );
}
