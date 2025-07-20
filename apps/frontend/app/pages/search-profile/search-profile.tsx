import { Book, FileText, Search, ChevronDown, ChevronUp } from "lucide-react";
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
import { ScrollArea } from "~/components/ui/scroll-area";
import {
  ArticlesSkeleton,
  SearchProfileSkeleton,
} from "./search-profile-skeleton";
import { useTranslation } from "react-i18next";
import { Button } from "~/components/ui/button";
import type { MatchesResponse, TopicMatch } from "types/model";
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

  const [showAllTopics, setShowAllTopics] = useState(false);
  const INITIAL_TOPICS_COUNT = 4;

  const [expandedArticleTopics, setExpandedArticleTopics] = useState<
    Set<string>
  >(new Set());
  const INITIAL_ARTICLE_TOPICS_COUNT = 2;

  const { t, i18n } = useTranslation();

  const [matches, setMatches] = useState<MatchesResponse | undefined>(
    undefined,
  );
  const [matchesLoading, setMatchesLoading] = useState<boolean>(false);
  const [imgError, setImgError] = useState(false);

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

  const getTopicsToDisplay = () => {
    if (!profile?.topics) return [];
    return showAllTopics
      ? profile.topics
      : profile.topics.slice(0, INITIAL_TOPICS_COUNT);
  };

  const hasMoreTopics =
    profile?.topics && profile.topics.length > INITIAL_TOPICS_COUNT;

  const getArticleTopicsToDisplay = (matchId: string, topics: TopicMatch[]) => {
    const isExpanded = expandedArticleTopics.has(matchId);
    return isExpanded ? topics : topics.slice(0, INITIAL_ARTICLE_TOPICS_COUNT);
  };

  const hasMoreArticleTopics = (topics: TopicMatch[]) => {
    return topics.length > INITIAL_ARTICLE_TOPICS_COUNT;
  };

  const toggleArticleTopics = (matchId: string) => {
    const newExpanded = new Set(expandedArticleTopics);
    if (newExpanded.has(matchId)) {
      newExpanded.delete(matchId);
    } else {
      newExpanded.add(matchId);
    }
    setExpandedArticleTopics(newExpanded);
  };

  return (
    <Layout>
      {!profile || isProfileLoading ? (
        <SearchProfileSkeleton />
      ) : (
        <div className="w-full flex flex-col pb-1">
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
            <Text hierachy={2}>{profile?.name}</Text>
            <div className="flex items-start justify-between mb-4 gap-10">
              <div className="grow">
                <div className="flex items-center gap-1 mb-2">
                  <Book className={"w-4 h-4"} />
                  <p className="font-bold">{t("search_profile.Topics")}</p>
                </div>

                <div className="flex flex-wrap gap-2">
                  {getTopicsToDisplay().map((topic, idx) => (
                    <div className="bg-gray-200 rounded-lg py-1 px-2" key={idx}>
                      {topic.name}
                    </div>
                  ))}
                  {hasMoreTopics && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowAllTopics(!showAllTopics)}
                      className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
                    >
                      {showAllTopics ? (
                        <>
                          {t("search_profile.show_less")}
                          <ChevronUp size={16} />
                        </>
                      ) : (
                        <>
                          {t("search_profile.show_more")} (
                          {profile.topics.length - INITIAL_TOPICS_COUNT}
                          {""})
                          <ChevronDown size={16} />
                        </>
                      )}
                    </Button>
                  )}
                </div>
              </div>
              <Button asChild>
                <Link to="reports">
                  <FileText />
                  {t("reports.reports")}
                </Link>
              </Button>
            </div>
          </div>

          <div className=" flex flex-row justify-start mt-2 mb-4 gap-3">
            <div className="w-1/5 min-w-[286px] h-full">
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
            <div className="w-4/5 flex flex-col pl-1 pt-1">
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
              <div className="bg-card rounded-lg border shadow-sm ">
                <ScrollArea className="p-2 h-[1200px]">
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

                      const topicsToShow = getArticleTopicsToDisplay(
                        match.id,
                        match.topics,
                      );
                      const hasMoreTopicsForArticle = hasMoreArticleTopics(
                        match.topics,
                      );
                      const isExpanded = expandedArticleTopics.has(match.id);

                      return (
                        <Link to={`./${match.id}`} key={match.id}>
                          <Card
                            className="mb-2 p-5 gap-3 justify-start"
                            key={match.id}
                          >
                            <div className="flex flex-row gap-2">
                              {!match.article.image_urls[0] || imgError ? (
                                <div className="w-[90px] h-[90px] rounded-md shadow-md border flex items-center justify-center text-muted-foreground text-sm shrink-0">
                                  {t("search_profile.no_image")}
                                </div>
                              ) : (
                                <img
                                  src={match.article.image_urls[0]}
                                  alt={getLocalizedContent(
                                    match.article.headline,
                                    i18n,
                                  )}
                                  className="w-[90px] h-[90px] object-cover rounded-md shadow-md shrink-0"
                                  onError={() => setImgError(true)}
                                />
                              )}
                              <div className="flex flex-col justify-evenly p-2">
                                <CardTitle className="text-xl line-clamp-2">
                                  {getLocalizedContent(
                                    match.article.headline,
                                    i18n,
                                  )}
                                </CardTitle>
                                <p className="line-clamp-2 text-gray-700 text-sm">
                                  {getLocalizedContent(
                                    match.article.summary,
                                    i18n,
                                  )}
                                </p>
                              </div>
                            </div>
                            <div className="flex gap-3 items-center flex-wrap">
                              <div
                                className={`rounded-lg py-1 px-2 ${bgColor} text-sm`}
                              >
                                {t("search_profile.Relevance")}{" "}
                                {getPercentage(relevance)}
                              </div>
                              {topicsToShow.map((topic) => (
                                <div
                                  className="bg-gray-200 rounded-lg py-1 px-2 shrink-0 text-sm"
                                  key={topic.id}
                                >
                                  {getPercentage(topic.score) +
                                    " " +
                                    topic.name}
                                </div>
                              ))}
                              {hasMoreTopicsForArticle && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={(e) => {
                                    e.preventDefault();
                                    toggleArticleTopics(match.id);
                                  }}
                                  className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
                                >
                                  {isExpanded ? (
                                    <>
                                      {t("search_profile.show_less")}
                                      <ChevronUp size={16} />
                                    </>
                                  ) : (
                                    <>
                                      {t("search_profile.show_more")} (
                                      {match.topics.length -
                                        INITIAL_ARTICLE_TOPICS_COUNT}
                                      )
                                      <ChevronDown size={16} />
                                    </>
                                  )}
                                </Button>
                              )}
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
      )}
    </Layout>
  );
}
