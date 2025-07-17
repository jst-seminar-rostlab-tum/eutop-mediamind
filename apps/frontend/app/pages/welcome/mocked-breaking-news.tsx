import { BreakingNewsCard } from "~/custom-components/breaking-news/breaking-news-card";
import { useTranslation } from "react-i18next";
import Text from "~/custom-components/text";
import { sortBy } from "lodash-es";

export function MockedBreakingNews() {
  const { t } = useTranslation();

  const news = [
    {
      id: "1",
      title:
        "Breakthrough in Sustainable Tire Technology Reduces Microplastic Emissions",
      summary:
        "A German startup has developed a biodegradable tire compound that significantly reduces microplastic emissions without compromising performance. Early tests show a 40% drop in road wear particles.",
      image_url: "https://picsum.photos/800/600?random=1",
      url: "",
      published_at: "2025-07-16T09:00:00Z",
    },
    {
      id: "2",
      title: "EU Announces New Incentives for Hydrogen Truck Adoption",
      summary:
        "The European Commission unveiled a subsidy program aimed at accelerating the transition to hydrogen-powered freight transport, with up to €150,000 available per vehicle for eligible operators.",
      image_url: "https://picsum.photos/800/600?random=2",
      url: "",
      published_at: "2025-07-15T13:30:00Z",
    },
    {
      id: "3",
      title:
        "French Automotive Supplier Launches AI-Driven Battery Diagnostics Platform",
      summary:
        "ValeonTech has introduced a new software solution for EV manufacturers that leverages AI to predict battery degradation and optimize charging behavior over time.",
      image_url: "https://picsum.photos/800/600?random=3",
      url: "",
      published_at: "2025-07-14T08:45:00Z",
    },
    {
      id: "4",
      title: "Norway's Offshore Wind Expansion Set to Power 2 Million Homes",
      summary:
        "Norway's government has approved funding for a 6.5 GW offshore wind farm in the North Sea, expected to begin construction in 2026. The project will be one of the largest of its kind in Europe.",
      image_url: "https://picsum.photos/800/600?random=4",
      url: "",
      published_at: "2025-07-13T10:15:00Z",
    },
    {
      id: "5",
      title:
        "Recycled Carbon Fiber Gains Traction in Automotive Lightweighting",
      summary:
        "A new report highlights the growing use of recycled carbon fiber composites in vehicle manufacturing, citing cost reduction, supply chain resilience, and sustainability benefits.",
      image_url: "https://picsum.photos/800/600?random=5",
      url: "",
      published_at: "2025-07-12T11:50:00Z",
    },
  ];

  const sortedNews = sortBy(news ?? [], "created_at").reverse();

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
