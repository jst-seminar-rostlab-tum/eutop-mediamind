import { Book, FileText, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { Card, CardTitle } from "~/components/ui/card";
import { Input } from "~/components/ui/input";
import Text from "~/custom-components/text";
import {
  getLocalizedContent,
  getPercentage,
  truncateAtWord,
} from "~/lib/utils";
import { MockedSidebarFilter } from "./mocked-sidebar-filter";
import { ScrollArea, ScrollBar } from "~/components/ui/scroll-area";
import { useTranslation } from "react-i18next";
import { Button } from "~/components/ui/button";
import { toast } from "sonner";
import { matches } from "./mock-data";

export function MockedSearchProfileOverview() {
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<"relevance" | "date">("relevance");

  const [searchSources, setSearchSources] = useState("");

  const [searchTopics, setSearchTopics] = useState("");

  const [fromDate, setFromDate] = useState<Date>();
  const [toDate, setToDate] = useState<Date>();

  const [searchTerm, setSearchTerm] = useState<string>("");

  const { t } = useTranslation();

  const profile = {
    id: "1",
    name: "Eutop",
    is_public: true,
    organization_emails: ["user@example.com"],
    profile_emails: ["user@example.com"],
    can_read_user_ids: ["1"],
    is_reader: true,
    can_edit_user_ids: ["1"],
    is_editor: true,
    owner_id: "1",
    is_owner: true,
    language: "en",
    topics: [
      {
        id: "1",
        name: "Automotive",
        keywords: ["Tires", "Engine"],
      },
      {
        id: "2",
        name: "Environment",
        keywords: ["CO2", "Renewable Energy"],
      },
    ],
    subscriptions: [
      {
        id: "1",
        name: "Spiegel",
        is_subscribed: true,
      },
      {
        id: "2",
        name: "Welt",
        is_subscribed: true,
      },
      {
        id: "3",
        name: "FAZ",
        is_subscribed: true,
      },
    ],
    new_articles_count: 3,
  };

  const [selectedTopics, setSelectedTopics] = useState<string[]>(
    profile.topics.map((s) => s.id),
  );
  const [selectedSources, setSelectedSources] = useState<string[]>(
    profile.subscriptions.map((s) => s.id),
  );

  const [filteredMatches, setFilteredMatches] = useState(matches);

  useEffect(() => {
    const from = fromDate ?? new Date("1900-01-01");
    const to = toDate ?? new Date("9999-12-31");

    const filtered = matches.filter((match) => {
      const date = new Date(match.article.date);

      // Date filter
      if (date < from || date > to) return false;

      // Search term in headline or summary
      const content =
        getLocalizedContent(match.article.headline) +
        getLocalizedContent(match.article.summary);

      if (
        searchTerm &&
        !content.toLowerCase().includes(searchTerm.toLowerCase())
      ) {
        return false;
      }

      // Topics filter
      if (
        selectedTopics.length > 0 &&
        !match.topics.some((t) => selectedTopics.includes(t.id))
      ) {
        return false;
      }

      // Source filter (based on article.source)
      if (
        selectedSources.length == 0 ||
        !selectedSources.includes(match.article.source)
      ) {
        return false;
      }

      return true;
    });

    // Sorting
    const sorted = [...filtered].sort((a, b) => {
      if (sortBy === "date") {
        return (
          new Date(b.article.date).getTime() -
          new Date(a.article.date).getTime()
        );
      } else {
        return b.relevance - a.relevance;
      }
    });

    setFilteredMatches(sorted);
  }, [fromDate, toDate, sortBy, searchTerm, selectedTopics, selectedSources]);

  const Sources = profile ? profile.subscriptions : [];
  const Topics = profile ? profile.topics : [];

  return (
    <div className="w-full grow flex flex-col overflow-hidden">
      <div className="w-full flex flex-col justify-start">
        <div className="flex gap-6 items-center">
          <Text hierachy={2}>{profile?.name}</Text>
        </div>
        <div className="flex items-center justify-between mb-4 gap-10">
          <ScrollArea className="grow overflow-x-hidden whitespace-nowrap rounded-md pb-1.5">
            <div className="flex w-max space-x-2 p-1">
              <div className="flex items-center gap-1 shrink-0">
                <Book size={20} />
                <p className="font-bold">{t("search_profile.Topics")}</p>
              </div>
              {profile?.topics?.map((topic, idx) => (
                <div
                  className="bg-gray-200 rounded-lg py-1 px-2 shrink-0"
                  key={idx}
                >
                  {topic.name}
                </div>
              ))}
            </div>
            <ScrollBar orientation="horizontal" />
          </ScrollArea>
          <Button asChild>
            <span
              className="inline-flex items-center gap-2"
              onClick={() => toast.info(t("landing_page.click_reports"))}
            >
              <FileText />
              {t("reports.reports")}
            </span>
          </Button>
        </div>
      </div>

      <div className="overflow-hidden grow flex flex-row justify-start mt-2 mb-4 gap-8">
        <div className="max-w-[400px] h-full">
          <MockedSidebarFilter
            sortBy={sortBy}
            setSortBy={setSortBy}
            selectedSources={selectedSources}
            setSelectedSources={setSelectedSources}
            searchSources={searchSources}
            setSearchSources={setSearchSources}
            Sources={Sources}
            selectedTopics={selectedTopics}
            setSelectedTopics={setSelectedTopics}
            searchTopics={searchTopics}
            setSearchTopics={setSearchTopics}
            Topics={Topics}
            fromDate={fromDate}
            setFromDate={setFromDate}
            toDate={toDate}
            setToDate={setToDate}
          />
        </div>
        <div className="min-w-[500px] grow flex flex-col overflow-hidden">
          <div className="relative mb-4 w-full flex">
            <Input
              placeholder={t("Search") + " " + t("search_profile.articles")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <Button
              variant="default"
              className="rounded-m ml-2"
              onClick={() => setSearchTerm(search)}
            >
              <Search />
            </Button>
          </div>
          <div className="bg-card rounded-lg border shadow-sm grow overflow-hidden">
            <div className="h-full">
              <ScrollArea className="p-4 h-full">
                {filteredMatches.map((match) => {
                  const relevance = match.relevance;

                  const bgColor =
                    relevance > 0.7
                      ? "bg-green-200"
                      : relevance < 0.3
                        ? "bg-red-200"
                        : "bg-yellow-200";

                  return (
                    <Card
                      className="mb-4 p-5 gap-4 justify-start"
                      key={match.id}
                    >
                      <div className="flex flex-row gap-4">
                        <img
                          src={match.article.image_urls[0]}
                          alt={getLocalizedContent(match.article.headline)}
                          className="w-[130px] h-[130px] object-cover rounded-md shadow-md shrink-0"
                        />
                        <div className="flex flex-col justify-evenly gap-4 p-2">
                          <CardTitle className="text-xl">
                            {getLocalizedContent(match.article.headline)}
                          </CardTitle>
                          <p>
                            {truncateAtWord(
                              getLocalizedContent(match.article.summary),
                              190,
                            )}
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-3 items-center">
                        <div className={`rounded-lg py-1 px-2 ${bgColor}`}>
                          {t("search_profile.Relevance")}{" "}
                          {getPercentage(relevance)}
                        </div>
                        {match.topics.map((topic) => (
                          <div
                            className="bg-gray-200 rounded-lg py-1 px-2"
                            key={topic.id}
                          >
                            {getPercentage(topic.score) + " " + topic.name}
                          </div>
                        ))}
                      </div>
                    </Card>
                  );
                })}
              </ScrollArea>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
