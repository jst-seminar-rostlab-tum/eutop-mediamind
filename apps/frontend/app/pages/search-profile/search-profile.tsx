import { Book, FileText, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router";
import { client, useQuery } from "types/api";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "~/components/ui/breadcrumb";
import { Card, CardTitle } from "~/components/ui/card";
import { Input } from "~/components/ui/input";
import Layout from "~/custom-components/layout";
import Text from "~/custom-components/text";
import { getLocalizedContent, getPercentage } from "~/lib/utils";
import { useNavigate } from "react-router";
import { SidebarFilter } from "./sidebar-filter";
import { ScrollArea, ScrollBar } from "~/components/ui/scroll-area";
import {
  ArticlesSkeleton,
  SearchProfileSkeleton,
} from "./search-profile-skeleton";
import { useTranslation } from "react-i18next";
import { Button } from "~/components/ui/button";
import type { MatchesResponse } from "types/model";
import { toast } from "sonner";

const suppressSWRReloading = {
  refreshInterval: 0,
  refreshWhenHidden: false,
  revalidateOnFocus: false,
  refreshWhenOffline: false,
  revalidateIfStale: false,
  revalidateOnReconnect: false,
};

export function SearchProfileOverview() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<"relevance" | "date">("relevance");

  const [searchSources, setSearchSources] = useState("");

  const [searchTopics, setSearchTopics] = useState("");

  const [fromDate, setFromDate] = useState<Date>();
  const [toDate, setToDate] = useState<Date>();
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [profileReady, setProfileReady] = useState<boolean>(false);

  const [searchTerm, setSearchTerm] = useState<string>("");

  const { t } = useTranslation();

  const [matches, setMatches] = useState<MatchesResponse | undefined>(
    undefined,
  );
  const [matchesLoading, setMatchesLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!id) {
      navigate("/error/404");
    }
  }, [id, navigate]);

  const {
    data: profile,
    isLoading: isProfileLoading,
    error: profileError,
  } = useQuery(
    "/api/v1/search-profiles/{search_profile_id}",
    { params: { path: { search_profile_id: id! } } },
    suppressSWRReloading,
  );

  useEffect(() => {
    if (profileError) {
      navigate("/error/404");
    }
  }, [profileError, navigate]);

  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);

  useEffect(() => {
    //init base matches search for first POST
    if (!profileError && profile && profile.subscriptions && profile.topics) {
      const subscriptionIds = profile.subscriptions.map((s) => s.id);
      const topicsIds = profile.topics.map((s) => s.id);
      setSelectedSources(subscriptionIds);
      setSelectedTopics(topicsIds);

      setFromDate(yesterday);
      setToDate(today);

      setProfileReady(true);
    }
  }, [profile, profileError]);

  useEffect(() => {
    if (!profileReady) return;
    setMatchesLoading(true);

    const requestBody = {
      startDate: fromDate
        ? fromDate.toISOString().split("T")[0]
        : yesterday.toISOString().split("T")[0],
      endDate: toDate
        ? toDate.toISOString().split("T")[0]
        : today.toISOString().split("T")[0],
      sorting: sortBy.toUpperCase() as "DATE" | "RELEVANCE",
      searchTerm: searchTerm,
      topics: selectedTopics,
      subscriptions: selectedSources,
    };
    client
      .POST("/api/v1/search-profiles/{search_profile_id}/matches", {
        params: {
          path: { search_profile_id: id! },
        },
        body: requestBody,
      })
      .then(({ data, error }) => {
        if (data) {
          setMatches(data);
          setMatchesLoading(false);
        } else if (error) {
          toast.error(t("search_profile.articles_error"));
          console.error("Error fetching matches:", error);
        }
      });
  }, [
    id,
    fromDate,
    toDate,
    sortBy,
    searchTerm,
    selectedTopics,
    selectedSources,
  ]);

  const Sources = profile ? profile.subscriptions : [];
  const Topics = profile ? profile.topics : [];

  const image_urls = [
    "https://picsum.photos/800/600?random=1",
    "https://picsum.photos/800/600?random=2",
    "https://picsum.photos/800/600?random=3",
    "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&h=600",
    "https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=800&h=600",
  ];

  return (
    <Layout className="flex justify-center" noOverflow={true}>
      {!profile || isProfileLoading ? (
        <SearchProfileSkeleton />
      ) : (
        <div className="w-full grow flex flex-col overflow-hidden">
          <div className="w-full flex flex-col justify-start">
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem>
                  <BreadcrumbLink asChild>
                    <Link to="/dashboard">{t("breadcrumb_home")}</Link>
                  </BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                  <BreadcrumbPage>{profile?.name}</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
            <div className="flex gap-6 items-center">
              <Text hierachy={2}>{profile?.name}</Text>
              <div className="bg-blue-200 etext-blue-900 font-bold rounded-full h-8 flex items-center justify-center text-sm shadow-sm p-4">
                {profile.new_articles_count} {t("search_profile.New_Articles")}
              </div>
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
                <Link to="reports">
                  <FileText />
                  {t("reports.reports")}
                </Link>
              </Button>
            </div>
          </div>

          <div className="overflow-hidden grow flex flex-row justify-start mt-2 mb-4 gap-8">
            <div className="max-w-[400px] h-full">
              <SidebarFilter
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
                    {!matches || matchesLoading ? (
                      <ArticlesSkeleton />
                    ) : matches?.matches.length === 0 ? (
                      <p className="text-muted-foreground text-sm text-center pt-2 italic">
                        {t("search_profile.No_articles")}
                      </p>
                    ) : (
                      matches?.matches.map((match) => {
                        const relevance = match.relevance;

                        const bgColor =
                          relevance > 0.7
                            ? "bg-green-200"
                            : relevance < 0.3
                              ? "bg-red-200"
                              : "bg-yellow-200";

                        return (
                          <Link to={`./${match.id}`}>
                            <Card
                              className="mb-4 p-5 gap-4 justify-start"
                              key={match.id}
                            >
                              <div className="flex flex-row gap-4">
                                <img
                                  src={image_urls[0]} //{match.article.image_urls[0]}
                                  alt="No Image"
                                  width={180}
                                  height={180}
                                  className="rounded-md"
                                />
                                <div className="flex flex-col justify-evenly gap-4">
                                  <CardTitle className="text-xl line-clamp-2">
                                    {getLocalizedContent(
                                      match.article.headline,
                                    )}
                                  </CardTitle>
                                  <p className="line-clamp-3">
                                    {getLocalizedContent(match.article.summary)}
                                  </p>
                                </div>
                              </div>
                              <div className="flex gap-3 items-center">
                                <div
                                  className={`rounded-lg py-1 px-2 ${bgColor}`}
                                >
                                  {t("search_profile.Relevance")}{" "}
                                  {getPercentage(relevance)}
                                </div>
                                {match.topics.map((topic) => (
                                  <div
                                    className="bg-gray-200 rounded-lg py-1 px-2 shrink-0"
                                    key={topic.id}
                                  >
                                    {getPercentage(topic.score) +
                                      " " +
                                      topic.name}
                                  </div>
                                ))}
                              </div>
                            </Card>
                          </Link>
                        );
                      })
                    )}
                  </ScrollArea>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
